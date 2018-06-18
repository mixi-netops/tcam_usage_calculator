import re


class Config:
    """
    path: String
        router config filepath.
    """
    def __init__(self, path):
        self.raw = None
        self.path = path

        self.read()

    def read(self):
        try:
            f = open(self.path, 'r')
        except FileNotFoundError as e:
            print(e, 'error occurred')
            quit(1)

        config = f.read()
        f.close()

        self.raw = config

    def get_firewall_line_list(self):
        firewall_line_list = []

        for line in self.raw.split('\n'):
            if line.find('set firewall family inet') >= 0:
                firewall_line_list.append(line)

        return firewall_line_list

    """
    Extract the term defined in a specific filter

    filterName: String
    termName: String
    """
    def get_term_line_list(self, filter_name, term_name):
        term_line_list = []

        for line in self.get_firewall_line_list():
            pattern = f"{'^.*' + filter_name + '.*' + term_name + '.*$'}"
            if not re.match(pattern, line):
                continue
            else:
                term_line_list.append(line)

        return term_line_list

    """
    Extract the 'prefix-list' defined in a specific filter

    prefixListName: String
    """
    def get_prefix_list_line_list(self, prefix_list_name):
        prefix_list_line_list = []
        pattern = f"{'set policy-options prefix-list ' + prefix_list_name}"

        for line in self.raw.split('\n'):
            if line.find(pattern) >= 0:
                prefix_list_line_list.append(line)

        return prefix_list_line_list
