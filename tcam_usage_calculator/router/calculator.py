import re
from ipaddress import summarize_address_range, IPv4Address

from .config import Config
from .port import Port
from ..util import err


class Calculator:
    """
    config: Config
        router config parameter.
    """
    def __init__(self, config):
        if type(config) is not Config:
            err(str(type(config)) + ' is not Config Class.')
        self.config = config

        self._firewall_cost_dict = {}
        self._total_cost = 0

        self.firewall_dict = self.__init_firewall_dict()

    """
    FirewallDict Design:
        {filter_name:[termName:ExpandedTermCost]}
        ex){'filterA':[{'termA1':0},{'termA2':0}], filterB:[{'termB1':0}]}
    """
    def __init_firewall_dict(self):
        firewall_dict = {}
        filter_and_term_name_pattern = r'^.* filter ([!-~]+) term ([!-~]+) .*$'

        def __has_term(_firewall_dict, _filter_name, _term_name):
            term_list = _firewall_dict[_filter_name]
            for term in term_list:
                if _term_name in term:
                    return True

            return False

        for line in self.config.firewall_lines:
            match = re.search(filter_and_term_name_pattern, line)
            filter_name = match.group(1)
            term_name = match.group(2)

            if filter_name not in firewall_dict:
                firewall_dict[filter_name] = [{term_name: 0}]
            else:
                exist_term = __has_term(_firewall_dict=firewall_dict, _filter_name=filter_name, _term_name=term_name)
                if not exist_term:
                    firewall_dict[filter_name].append({term_name: 0})

        self.__set_expanded_term_cost(firewall_dict)
        return firewall_dict

    def __set_expanded_term_cost(self, firewall_dict):
        for filter_name, terms in firewall_dict.items():
            self.config.filter_name = filter_name
            for term_dict in terms:
                for term_name in term_dict:
                    self.config.term_name = term_name
                    raw_expanded_term_cost = \
                        self.__get_term_src_prefix_count() * \
                        self.__get_term_dst_prefix_count() * \
                        self.__get_term_protocol_count() / \
                        self.__get_term_next_header_count() * \
                        self.__get_term_src_port_count() * \
                        self.__get_term_dst_port_count()

                    term_dict[term_name] = round(raw_expanded_term_cost)

    def __get_term_src_prefix_count(self):
        count = 1
        src_prefix_list_pattern = \
            r'^.*from source-prefix-list ([!-~]+)$'

        for line in self.config.term_lines:
            if re.match(src_prefix_list_pattern, line):
                match = re.search(src_prefix_list_pattern, line)
                self.config.prefix_list_name = match.group(1)
                count = len(self.config.prefix_list_line_list)

        return count

    def __get_term_dst_prefix_count(self):
        count = 1
        dst_prefix_list_pattern = \
            r'^.*from destination-prefix-list ([!-~]+)$'

        for line in self.config.term_lines:
            if re.match(dst_prefix_list_pattern, line):
                match = re.search(dst_prefix_list_pattern, line)
                self.config.prefix_list_name = match.group(1)
                count = len(self.config.prefix_list_line_list)

        return count

    def __get_term_protocol_count(self):
        count = 0
        protocol_pattern = \
            r'^.*from protocol [!-~]+$'

        for line in self.config.term_lines:
            if re.match(protocol_pattern, line):
                count += 1

        if count is 0:
            return 1

        return count

    def __get_term_next_header_count(self):
        count = 0
        next_header_pattern = \
            r'^.*from next-header [!-~]+$'

        for line in self.config.term_lines:
            if re.match(next_header_pattern, line):
                count += 1

        if count is 0:
            return 1

        return count

    def __get_term_src_port_count(self):
        port_list = []
        src_port_pattern = \
            r'^.*from source-port ([!-~]+)$'

        for line in self.config.term_lines:
            if re.match(src_port_pattern, line):
                match = re.search(src_port_pattern, line)
                raw_port = match.group(1)
                port_list.append(int(Port.translate_name2number(raw_port)))

        return self.__get_port_count(port_list)

    def __get_term_dst_port_count(self):
        port_list = []
        dst_port_pattern = \
            r'^.*from destination-port ([!-~]+)$'

        for line in self.config.term_lines:
            if re.match(dst_port_pattern, line):
                match = re.search(dst_port_pattern, line)
                raw_port = match.group(1)
                port_list.append(int(Port.translate_name2number(raw_port)))

        return self.__get_port_count(port_list)

    """
    portList:
        TCP/IP port list.

    Calculate considering consecutive port optimization.
    """
    def __get_port_count(self, port_list):
        port_listlen = len(port_list)
        if port_listlen <= 1:
            return 1

        # search consecutive port
        port_list.sort()
        count = 0
        while (port_listlen >= 2):
            start_index = 0
            end_index = 0

            for i in range(1, port_listlen):
                if (port_list[start_index] + i) == port_list[i]:
                    end_index = i
                else:
                    break

            if start_index is not end_index:
                summarize = list(summarize_address_range(IPv4Address(port_list[start_index]), IPv4Address(port_list[end_index])))
                count += len(summarize)
                del port_list[start_index:(end_index + 1)]
            else:
                del port_list[0:2]
                count += 2

            port_listlen = len(port_list)

        # If it is 1 port remaining, count as it is
        if port_listlen is 1:
            count += 1

        return count

    def __get_interface_cost(self, filter_name):
        cost = 0
        has_loopback_interface = False
        has_general_interface = False

        interface_pattern = \
            f"{'^set interfaces ([!-~]+) .*' + filter_name + '$'}"
        loopbackinterface_pattern = \
            f"{'^lo[0-9]+.*$'}"

        for line in self.config.raw.split('\n'):
            if not re.match(interface_pattern, line):
                continue
            else:
                match = re.search(interface_pattern, line)
                interface = match.group(1)

                # is loopback interface
                if re.match(loopbackinterface_pattern, interface):
                    has_loopback_interface = True
                else:
                    has_general_interface = True

        if has_loopback_interface:
            cost += 4
            if has_general_interface:
                cost += 1
        else:
            cost += 1

        return cost

    """
        firewall_cost_dict Design:
            {filter_name:cost}
            ex){'filterA':100, filterB:200}
    """
    @property
    def firewall_cost_dict(self):
        for filter_name, terms in self.firewall_dict.items():
            firewall_cost = 0
            for term in terms:
                for cost in term.values():
                    firewall_cost += cost

            interface_cost = self.__get_interface_cost(filter_name)
            self._firewall_cost_dict[filter_name] = firewall_cost * interface_cost

        return self._firewall_cost_dict

    @property
    def total_term_cost(self):
        if self._total_cost is not 0:
            self._total_cost = 0

        for cost in self.firewall_cost_dict.values():
            self._total_cost += cost

        return self._total_cost
