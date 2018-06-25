import re
from ..util import err


class Config:
    """
    path: String
        router config filepath.
    """
    def __init__(self, path):
        self.path = path
        self.raw = self.__read()

        self.firewall_line_list = self.__init_firewall_line_list()

        self.filter_name = None
        self.term_name = None
        self.prefix_list_name = None

        self._term_line_list = []
        self._prefix_list_line_list = []

    def __read(self):
        try:
            with open(self.path, 'r') as file:
                config = file.read()
        except FileNotFoundError as e:
            err(self.path + ' not found.')

        return config

    def __init_firewall_line_list(self):
        firewall_line_list = []

        for line in self.raw.split('\n'):
            if line.find('set firewall family inet') >= 0:
                firewall_line_list.append(line)

        return firewall_line_list

    @property
    def term_line_list(self):
        if self._term_line_list is not []:
            self._term_line_list = []

        pattern = f"{'^.*' + self.filter_name + '.*' + self.term_name + '.*$'}"

        for line in self.firewall_line_list:
            if not re.match(pattern, line):
                continue
            else:
                self._term_line_list.append(line)

        return self._term_line_list

    @property
    def prefix_list_line_list(self):
        if self._prefix_list_line_list is not []:
            self._prefix_list_line_list = []

        pattern = f"{'set policy-options prefix-list ' + self.prefix_list_name}"
        for line in self.raw.split('\n'):
            if line.find(pattern) >= 0:
                self._prefix_list_line_list.append(line)

        return self._prefix_list_line_list
