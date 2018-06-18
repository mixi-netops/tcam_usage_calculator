# tcam_usage_calculator
tcam_usage_calculator はルータの Config を読み込み、TCAM の使用量を予測するツールです。  
ただし、tcam_usage_calculator の予測は完璧ではなく、動作保証はしませんので自己責任で利用してください。  
本ツールは [Junos OS](https://www.juniper.net/jp/jp/products-services/nos/junos/) に対応しており、主にFirewallの定義から使用量の予測を行っています。

## 動作環境
* Pyhton 3.6 以上

## セットアップ
```bash
$ pip install git+https://github.com/xflagstudio/tcam_usage_calculator.git
```

### Docker
```bash
$ docker build -t xflagstudio/tcam_usage_calculator:1.0 .
```

## 使い方
Config 全体の TCAM 使用量を確認する
```bash
$ tcam_usage_calculator /path/to/config/RouterConfig
TotalCost: 225
```

Config 全体と Filter 毎の TCAM 使用量を確認する
```bash
$ tcam_usage_calculator /path/to/config/RouterConfig -d
filterA: 30
filterB: 3
filterC: 32
TotalCost: 65
```

特定の Filter の TCAM 使用量を確認する
```bash
$ tcam_usage_calculator /path/to/config/RouterConfig -f filterA
filterA: 30

$ tcam_usage_calculator /path/to/config/RouterConfig -f filterA filterC
filterA: 30
filterC: 32
```

出力フォーマットをJSON形式にする
```bash
$ tcam_usage_calculator /path/to/config/RouterConfig -d -j
[{"filterA": 30}, {"filterB": 3}, {"filterC": 32}, {"TotalCost": 65}]

$ tcam_usage_calculator /path/to/config/RouterConfig -f filterA filterC -j
[{"filterA": 30}, {"filterC": 32}]
```

### Docker
```bash
$ CONFIG_FROM="/path/to/config/RouterConfig"
$ CONFIG_TO="/tmp/config"
$ docker run -v "$CONFIG_FROM:$CONFIG_TO" -it xflagstudio/tcam_usage_calculator:1.0 /bin/bash -c "tcam_usage_calculator -d -j $CONFIG_TO"
```

## ライセンス
[MIT license](https://github.com/xflagstudio/tcam_usage_calculator/blob/master/LICENSE)
