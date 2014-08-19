#Porter


> perillaroc-data-converter

简单的数据转码工具，用于将GRADS格式转换成MICPAS格式。

##安装

暂时直接使用porter.py脚本，还未实现安装功能。

##开始使用

1. 编写配置文件

参见test/grads2micaps目录下的配置文件

2. 运行脚本

```
python porter.py config-file-path
```
config-file-path为配置文件的路径。

##配置文件格式详解

```javascript
{
    "ctl": "path-to-ctl-file",
    "output_dir": "output-dir",
    "start_time": "YYYYMMDDHH",
    "forecast_time": "HHH",
    "records": [
        {
            "name": "variable name",
            "level": level_value,
            "level": "level_type(default multi)"
            "type": "type to be converted to (such as micaps.4)",
            "value": "value expr in which x is the original value(such sa 'x - 273.16')"
        },
    ]
}
```

##致谢

本项目参考两位前辈的相关转码程序，鉴于隐私问题，不能写出联系方式。感谢前辈们的精彩程序，让我受益匪浅。



