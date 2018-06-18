import re
from .config import Config
from socket import getservbyname
from ipaddress import summarize_address_range, IPv4Address


class Calculator:
    """
    config: Config
        router config parameter.
    """
    def __init__(self, config):
        if type(config) is not Config:
            nl = '\n'
            print(f"{'ERROR!' + nl}{config + 'is not Config Class.'}")
            quit(1)

        self.config = config

    """
    name: String
        filter name.
    """
    def has_filter(self, name):
        return name in self.filrewall_dict

    """
    filter_name: String
        filter name.
    termName: String
        term name.
    """
    def has_term(self, filter_name, term_name):
        term_list = self.filrewall_dict[filter_name]
        for term in term_list:
            if term_name in term:
                return True

        return False

    """
    FirewallDict Design:
        {filter_name:[termName:ExpandedTermCost]}
        ex){'filterA':[{'termA1':0},{'termA2':0}], filterB:[{'termB1':0}]}
    """
    def create_firewall_dict(self):
        self.filrewall_dict = {}
        filter_and_term_name_pattern = \
            r'^.* filter ([!-~]+) term ([!-~]+) .*$'

        for line in self.config.get_firewall_line_list():
            match = re.search(filter_and_term_name_pattern, line)
            filter_name = match.group(1)
            term_name = match.group(2)

            if not self.has_filter(filter_name):
                self.filrewall_dict[filter_name] = [{term_name: 0}]
            else:
                exist_term = self.has_term(filter_name, term_name)
                if not exist_term:
                    self.filrewall_dict[filter_name].append({term_name: 0})

    """
    This function is supposed to be executed after
    execution of createFirewallDict
    """
    def set_expanded_term_cost(self):
        for filter_name, terms in self.filrewall_dict.items():
            for term_dict in terms:
                for term_name in term_dict:
                    term_line_list = self.config.get_term_line_list(filter_name=filter_name, term_name=term_name)
                    raw_expanded_term_cost = \
                        self.get_term_src_prefix_count(term_line_list) * \
                        self.get_term_dst_prefix_count(term_line_list) * \
                        self.get_term_protocol_count(term_line_list) / \
                        self.get_term_next_header_count(term_line_list) * \
                        self.get_term_src_port_count(term_line_list) * \
                        self.get_term_dst_port_count(term_line_list)

                    term_dict[term_name] = round(raw_expanded_term_cost)

    def get_term_src_prefix_count(self, term_line_list):
        count = 1
        src_prefix_list_pattern = \
            r'^.*from source-prefix-list ([!-~]+)$'

        for line in term_line_list:
            if re.match(src_prefix_list_pattern, line):
                match = re.search(src_prefix_list_pattern, line)
                prefix_list_name = match.group(1)
                count = len(self.config.get_prefix_list_line_list(prefix_list_name))

        return count

    def get_term_dst_prefix_count(self, term_line_list):
        count = 1
        dst_prefix_list_pattern = \
            r'^.*from destination-prefix-list ([!-~]+)$'

        for line in term_line_list:
            if re.match(dst_prefix_list_pattern, line):
                match = re.search(dst_prefix_list_pattern, line)
                prefix_list_name = match.group(1)
                count = len(self.config.get_prefix_list_line_list(prefix_list_name))

        return count

    def get_term_protocol_count(self, term_line_list):
        count = 0
        protocol_pattern = \
            r'^.*from protocol [!-~]+$'

        for line in term_line_list:
            if re.match(protocol_pattern, line):
                count += 1

        if count is 0:
            return 1

        return count

    def get_term_next_header_count(self, term_line_list):
        count = 0
        next_header_pattern = \
            r'^.*from next-header [!-~]+$'

        for line in term_line_list:
            if re.match(next_header_pattern, line):
                count += 1

        if count is 0:
            return 1

        return count

    """
    name: String
        port name.
        ex) 'https'

    translat port name to number.
    If the name is a number, it returns as is.
    """
    def translat_port_number(self, name):
        if name.isdigit():
            return name

        return getservbyname(name)

    """
    portList:
        TCP/IP port list.

    Calculate considering consecutive port optimization.
    """
    def get_port_count(self, port_list):
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

    def get_term_src_port_count(self, term_line_list):
        port_list = []
        src_port_pattern = \
            r'^.*from source-port ([!-~]+)$'

        for line in term_line_list:
            if re.match(src_port_pattern, line):
                match = re.search(src_port_pattern, line)
                raw_port = match.group(1)
                port_list.append(int(self.translat_port_number(raw_port)))

        return self.get_port_count(port_list)

    def get_term_dst_port_count(self, term_line_list):
        port_list = []
        dst_port_pattern = \
            r'^.*from destination-port ([!-~]+)$'

        for line in term_line_list:
            if re.match(dst_port_pattern, line):
                match = re.search(dst_port_pattern, line)
                raw_port = match.group(1)
                port_list.append(int(self.translat_port_number(raw_port)))

        return self.get_port_count(port_list)

    def get_interface_cost(self, filter_name):
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
    def make_firewall_cost_dict(self):
        self.firewall_cost_dict = {}
        for filter_name, termList in self.filrewall_dict.items():
            firewall_cost = 0
            for term in termList:
                for cost in term.values():
                    firewall_cost += cost

            interface_cost = self.get_interface_cost(filter_name)
            self.firewall_cost_dict[filter_name] = firewall_cost * interface_cost

    def get_total_term_cost(self):
        total_cost = 0
        self.make_firewall_cost_dict()

        for cost in self.firewall_cost_dict.values():
            total_cost += cost

        return total_cost
