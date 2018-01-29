# tcam-usage-calculator
tcam-usage-calculator はルータの Config を読み込み、TCAM の使用量を予測するツールです。ただし、使用量の予測は完璧ではないことに注意してください。  
本ツールは [Junos OS](https://www.juniper.net/jp/jp/products-services/nos/junos/) に対応しており、主にFirewallの定義から使用量の予測を行っています。

## 動作環境
* Pyhton 3.6.4

## 使い方
Config 全体の TCAM 使用量を確認する
```bash
$ python main.py /path/to/config/RouterConfig
TotalCost: 225
```

Config 全体と Filter 毎の TCAM 使用量を確認する
```bash
$ python main.py /path/to/config/RouterConfig -d
filterA: 30
filterB: 3
filterC: 32
TotalCost: 65
```

特定の Filter の TCAM 使用量を確認する
```bash
$ python main.py /path/to/config/RouterConfig -f filterA
filterA: 30

$ python main.py /path/to/config/RouterConfig -f filterA filterC
filterA: 30
filterC: 32
```

出力フォーマットをJSON形式にする
```bash
$ python main.py /path/to/config/RouterConfig -d -j
[{"filterA": 30}, {"filterB": 3}, {"filterC": 32}, {"TotalCost": 65}]

$ python main.py /path/to/config/RouterConfig -f filterA filterC -j
[{"filterA": 30}, {"filterC": 32}]
```
