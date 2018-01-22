# Porter


> Porter is perillaroc-data-converter

简单的数据转码工具，用于将 GRADS 格式转换成 MICPAS 格式。

## 安装

暂时直接使用 `porter.py` 脚本，还未实现安装功能。

## 开始使用

1. 编写配置文件

参见 `test/grads2micaps` 目录下的配置文件

2. 运行脚本

```
python porter.py config-file-path-list
```

`config-file-path-list` 为配置文件列表。

## 配置文件

```json
{
    "ctl": "path-to-ctl-file",
    "output_dir": "output-dir",
    "start_time": "YYYYMMDDHH",
    "forecast_time": "HHH",
    "records": [
        {
            "name": "variable name",
            "level": level_value,
            "level_type": "level_type(default multi)"
            "target_type": "type to be converted to (such as micaps.4)",
            "value": "value expr in which x is the original value(such sa 'x - 273.16')"
        }
    ]
}
```

## 致谢

本项目参考两位前辈的相关转码程序，鉴于隐私问题，不能写出联系方式。感谢前辈们的精彩程序，让我受益匪浅。
