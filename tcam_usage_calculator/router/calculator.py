import re
from tcam_usage_calculator.router.config import Config
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
    def hasFilter(self, name):
        return name in self.filrewallDict

    """
    filterName: String
        filter name.
    termName: String
        term name.
    """
    def hasTerm(self, filterName, termName):
        termList = self.filrewallDict[filterName]
        for term in termList:
            if termName in term:
                return True

        return False

    """
    FirewallDict Design:
        {filterName:[termName:ExpandedTermCost]}
        ex){'filterA':[{'termA1':0},{'termA2':0}], filterB:[{'termB1':0}]}
    """
    def createFirewallDict(self):
        self.filrewallDict = {}
        filterAndTermNamePattern = \
            r'^.* filter ([!-~]+) term ([!-~]+) .*$'

        for line in self.config.getFirewallLineList():
            match = re.search(filterAndTermNamePattern, line)
            filterName = match.group(1)
            termName = match.group(2)

            if not self.hasFilter(filterName):
                self.filrewallDict[filterName] = [{termName: 0}]
            else:
                existTerm = self.hasTerm(filterName, termName)
                if not existTerm:
                    self.filrewallDict[filterName].append({termName: 0})

    """
    This function is supposed to be executed after
    execution of createFirewallDict
    """
    def setExpandedTermCost(self):
        for filterName, terms in self.filrewallDict.items():
            for termDict in terms:
                for termName in termDict:
                    termLineList = self.config.getTermLineList(filterName=filterName, termName=termName)
                    RawExpandedTermCost = \
                        self.getTermSrcPrefixCount(termLineList) *\
                        self.getTermDstPrefixCount(termLineList) *\
                        self.getTermProtocolCount(termLineList) /\
                        self.getTermNextHeaderCount(termLineList) *\
                        self.getTermSrcPortCount(termLineList) *\
                        self.getTermDstPortCount(termLineList)

                    termDict[termName] = round(RawExpandedTermCost)

    def getTermSrcPrefixCount(self, termLineList):
        count = 1
        srcPrefixListPattern = \
            r'^.*from source-prefix-list ([!-~]+)$'

        for line in termLineList:
            if re.match(srcPrefixListPattern, line):
                match = re.search(srcPrefixListPattern, line)
                prefixListName = match.group(1)
                count = len(self.config.getPrefixListLineList(prefixListName))

        return count

    def getTermDstPrefixCount(self, termLineList):
        count = 1
        dstPrefixListPattern = \
            r'^.*from destination-prefix-list ([!-~]+)$'

        for line in termLineList:
            if re.match(dstPrefixListPattern, line):
                match = re.search(dstPrefixListPattern, line)
                prefixListName = match.group(1)
                count = len(self.config.getPrefixListLineList(prefixListName))

        return count

    def getTermProtocolCount(self, termLineList):
        count = 0
        protocolPattern = \
            r'^.*from protocol [!-~]+$'

        for line in termLineList:
            if re.match(protocolPattern, line):
                count += 1

        if count is 0:
            return 1

        return count

    def getTermNextHeaderCount(self, termLineList):
        count = 0
        nextHeaderPattern = \
            r'^.*from next-header [!-~]+$'

        for line in termLineList:
            if re.match(nextHeaderPattern, line):
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
    def translatPortNumber(self, name):
        if name.isdigit():
            return name

        return getservbyname(name)

    """
    portList:
        TCP/IP port list.

    Calculate considering consecutive port optimization.
    """
    def getPortCount(self, portList):
        portListlen = len(portList)
        if portListlen <= 1:
            return 1

        # search consecutive port
        portList.sort()
        count = 0
        while (portListlen >= 2):
            startIndex = 0
            endIndex = 0

            for i in range(1, portListlen):
                if (portList[startIndex] + i) == portList[i]:
                    endIndex = i
                else:
                    break

            if startIndex is not endIndex:
                summarize = list(summarize_address_range(IPv4Address(portList[startIndex]), IPv4Address(portList[endIndex])))
                count += len(summarize)
                del portList[startIndex:(endIndex + 1)]
            else:
                del portList[0:2]
                count += 2

            portListlen = len(portList)

        # If it is 1 port remaining, count as it is
        if portListlen is 1:
            count += 1

        return count

    def getTermSrcPortCount(self, termLineList):
        portList = []
        srcPortPattern = \
            r'^.*from source-port ([!-~]+)$'

        for line in termLineList:
            if re.match(srcPortPattern, line):
                match = re.search(srcPortPattern, line)
                rawPort = match.group(1)
                portList.append(int(self.translatPortNumber(rawPort)))

        return self.getPortCount(portList)

    def getTermDstPortCount(self, termLineList):
        portList = []
        dstPortPattern = \
            r'^.*from destination-port ([!-~]+)$'

        for line in termLineList:
            if re.match(dstPortPattern, line):
                match = re.search(dstPortPattern, line)
                rawPort = match.group(1)
                portList.append(int(self.translatPortNumber(rawPort)))

        return self.getPortCount(portList)

    def getInterfaceCost(self, filterName):
        cost = 0
        hasLoopbackInterface = False
        hasGeneralInterface = False

        interfacePattern = \
            f"{'^set interfaces ([!-~]+) .*' + filterName + '$'}"
        loopbackinterfacePattern = \
            f"{'^lo[0-9]+.*$'}"

        for line in self.config.raw.split('\n'):
            if not re.match(interfacePattern, line):
                continue
            else:
                match = re.search(interfacePattern, line)
                interface = match.group(1)

                # is loopback interface
                if re.match(loopbackinterfacePattern, interface):
                    hasLoopbackInterface = True
                else:
                    hasGeneralInterface = True

        if hasLoopbackInterface:
            cost += 4
            if hasGeneralInterface:
                cost += 1
        else:
            cost += 1

        return cost

    """
        FirewallCostDict Design:
            {filterName:cost}
            ex){'filterA':100, filterB:200}
    """
    def makeFirewallCostDict(self):
        self.firewallCostDict = {}
        for filterName, termList in self.filrewallDict.items():
            firewallCost = 0
            for term in termList:
                for cost in term.values():
                    firewallCost += cost

            interfaceCost = self.getInterfaceCost(filterName)
            self.firewallCostDict[filterName] = firewallCost * interfaceCost

    def getTotalTermCost(self):
        totalCost = 0
        self.makeFirewallCostDict()

        for cost in self.firewallCostDict.values():
            totalCost += cost

        return totalCost
