# Porter

> Porter is perillaroc-data-converter

A simple data convert tool which is used to convert GRADS binary data to MICAPS data.

## Installation

Install porter using:

```bash
python setup.py install
```

## Getting started

1. Create a config file.

    See example config files in directory `test/grads2micaps`.

2. Run the `porter` command.

```
porter grads2micaps config-file-path-list
```

`config-file-path-list` is config file list。

## Config file

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
            "level_type": "level_type(default multi)",
            "target_type": "type to be converted to (such as micaps.4)",
            "value": "value expr in which x is the original value(such sa 'x - 273.16')"
        }
    ]
}
```

## Acknowledgements

`porter` refers to some transcoding projects created by two predecessors. 
Due to privacy issues, I can not write their contact information.  
Thanks to their wonderful programs, and I benefit from their codes greatly.

## License

Copyright &copy; 2014-2018 Perilla Roc.

`porter` is licensed under [The MIT License](https://opensource.org/licenses/MIT).
