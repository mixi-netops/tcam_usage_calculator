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

        self.firewall_lines = self.__init_firewall_line_list()

        self.filter_name = None
        self.term_name = None
        self.prefix_list_name = None

        self._term_lines = []
        self._prefix_list_lines = []

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
    def term_lines(self):
        if self._term_lines is not []:
            self._term_lines = []

        pattern = f"{'^.*' + self.filter_name + '.*' + self.term_name + '.*$'}"

        for line in self.firewall_lines:
            if not re.match(pattern, line):
                continue
            else:
                self._term_lines.append(line)

        return self._term_lines

    @property
    def prefix_list_line_list(self):
        if self._prefix_list_lines is not []:
            self._prefix_list_lines = []

        pattern = f"{'set policy-options prefix-list ' + self.prefix_list_name}"
        for line in self.raw.split('\n'):
            if line.find(pattern) >= 0:
                self._prefix_list_lines.append(line)

        return self._prefix_list_lines
