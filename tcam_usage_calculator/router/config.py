import os
import re


class Config:
    """
    path: String
        router config filepath.
    """
    def __init__(self, path):
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

    def getFirewallLineList(self):
        firewallLineList = []

        for line in self.raw.split('\n'):
            if line.find('set firewall family inet') >= 0:
                firewallLineList.append(line)

        return firewallLineList

    """
    Extract the term defined in a specific filter

    filterName: String
    termName: String
    """
    def getTermLineList(self, filterName, termName):
        termLineList = []

        for line in self.getFirewallLineList():
            pattern = f"{'^.*' + filterName + '.*' + termName + '.*$'}"
            if not re.match(pattern, line):
                continue
            else:
                termLineList.append(line)

        return termLineList

    """
    Extract the 'prefix-list' defined in a specific filter

    prefixListName: String
    """
    def getPrefixListLineList(self, prefixListName):
        prefixListLineList = []
        pattern = f"{'set policy-options prefix-list ' + prefixListName}"

        for line in self.raw.split('\n'):
            if line.find(pattern) >= 0:
                prefixListLineList.append(line)

        return prefixListLineList
