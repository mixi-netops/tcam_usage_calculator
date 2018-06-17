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

    config_filepath = args.config[0]
    calculator = Calculator(Config(config_filepath))
    calculator.create_firewall_dict()
    calculator.set_expanded_term_cost()

    result_list = []

    if args.detail:
        filter_list = args.filter
        calculator.make_firewall_cost_dict()
        for name, cost in calculator.firewall_cost_dict.items():
            result_list.append({name: cost})

    if args.filter:
        filter_list = args.filter
        calculator.make_firewall_cost_dict()
        for name, cost in calculator.firewall_cost_dict.items():
            if name in filter_list:
                result_list.append({name: cost})
    else:
        # TotalCost is not displayed only when the --filter option is enabled
        result_list.append({"TotalCost": calculator.get_total_term_cost()})

    if args.json:
        print(json.dumps(result_list))
    else:
        for cost_dict in result_list:
            for name, cost in cost_dict.items():
                print(f"{name + ': ' + str(cost)}")


if __name__ == '__main__':
    main()
