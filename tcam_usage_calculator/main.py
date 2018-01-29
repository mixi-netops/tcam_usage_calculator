from tcam_usage_calculator.router.config import Config
from tcam_usage_calculator.router.calculator import Calculator
from argparse import ArgumentParser
import json


def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--filter", nargs='+', help="filter name")
    group.add_argument("-d", "--detail",  action="store_true",
                       help="print detail")
    parser.add_argument("config", nargs=1, help="router config file path")
    parser.add_argument("-j", "--json", action="store_true", help="json mode")
    args = parser.parse_args()

    configFilepath = args.config[0]
    calculator = Calculator(Config(configFilepath))
    calculator.createFirewallDict()
    calculator.setExpandedTermCost()

    resultList = []

    if args.detail:
        filterList = args.filter
        calculator.makeFirewallCostDict()
        for name, cost in calculator.firewallCostDict.items():
            resultList.append({name: cost})

    if args.filter:
        filterList = args.filter
        calculator.makeFirewallCostDict()
        for name, cost in calculator.firewallCostDict.items():
            if name in filterList:
                resultList.append({name: cost})
    else:
        # TotalCost is not displayed only when the --filter option is enabled
        resultList.append({"TotalCost": calculator.getTotalTermCost()})

    if args.json:
        print(json.dumps(resultList))
    else:
        for costDict in resultList:
            for name, cost in costDict.items():
                print(f"{name + ': ' + str(cost)}")


if __name__ == '__main__':
    main()
