# tcam-usage-calculator
tcam-usage-calculator is a tool to read Config of the router and predict TCAM usage.  
However, the prediction of tcam-usage-calculator is not perfect and we do not guarantee the operation, so please use it at your own risk.  
This tool is compatible with [Junos OS](https://www.juniper.net/jp/jp/products-services/nos/junos/), predict the usage mainly from the definition of Firewall.

## Operating environment
* Pyhton 3.6.4

## How to use
Confirm TCAM usage of whole Config
```bash
$ python main.py /path/to/config/RouterConfig
TotalCost: 225
```

Confirm TCAM usage of the whole Config and Filter
```bash
$ python main.py /path/to/config/RouterConfig -d
filterA: 30
filterB: 3
filterC: 32
TotalCost: 65
```

Confirm TCAM usage of specific Filter
```bash
$ python main.py /path/to/config/RouterConfig -f filterA
filterA: 30

$ python main.py /path/to/config/RouterConfig -f filterA filterC
filterA: 30
filterC: 32
```

Make output format JSON format
```bash
$ python main.py /path/to/config/RouterConfig -d -j
[{"filterA": 30}, {"filterB": 3}, {"filterC": 32}, {"TotalCost": 65}]

$ python main.py /path/to/config/RouterConfig -f filterA filterC -j
[{"filterA": 30}, {"filterC": 32}]
```
