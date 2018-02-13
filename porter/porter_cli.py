# coding=utf-8
"""
porter: a tool for GrADS data converting
"""
from __future__ import print_function, absolute_import
import os
import json
import datetime
import time
import click

from porter.grads2micaps import Grads2Micaps
from porter.grads_ctl_parser import GradsCtlParser, GradsCtl


class Porter:
    def __init__(self):
        pass

    def print_record_info(self, record):
        print("[{class_name}] Converting {name} with level {level} to {target_type}...".format(
            class_name=self.__class__.__name__,
            name=record["name"],
            level=record["level"],
            target_type=record["target_type"]
        ), end='')
        pass

    def convert(self, config_file_path):
        with open(config_file_path) as config_file:
            config_str = config_file.read()
            config_object = json.loads(config_str, encoding='utf-8')

            ctl_file_path = os.path.abspath(config_object['ctl'])
            grads_ctl = GradsCtl()

            # output parser
            output_dir = os.path.abspath(config_object['output_dir'])

            # time parser
            start_time_str = config_object.get('start_time', '')
            forecast_time_str = config_object.get('forecast_time', '')
            if start_time_str != "":
                str_length = len(start_time_str)
                if str_length == 10:
                    start_time = datetime.datetime.strptime(start_time_str, "%Y%m%d%H")
                    grads_ctl.start_time = start_time
                else:
                    print("parser start_time error: %s" % start_time_str)

            if forecast_time_str != "":
                # TODO (windroc, 2014.08.18): use format:
                #   XXXhXXmXXs
                if len(forecast_time_str) == 3:
                    forecast_time = datetime.timedelta(hours=int(forecast_time_str))
                    grads_ctl.forecast_time = forecast_time

            # ctl parser
            grads_ctl_parser = GradsCtlParser(grads_ctl)
            grads_ctl = grads_ctl_parser.parse(ctl_file_path)

            # record parser
            records = config_object['records']
            for a_record in records:
                target_type = a_record["target_type"]

                self.print_record_info(a_record)

                def convert_a_record():
                    if target_type.startswith("micaps"):
                        grads_to_micaps = Grads2Micaps(grads_ctl)
                        a_record['output_dir'] = output_dir
                        grads_to_micaps.convert(a_record)
                    else:
                        print("Not implemented for %s" % target_type)
                time1 = time.clock()
                convert_a_record()
                time2 = time.clock()
                print("%.2fs" % (time2 - time1))


@click.group()
def cli():
    pass


@cli.command(help="convert GrADS data to MICAPS type 4 data.")
@click.argument("config-file", nargs=-1, required=True)
def grads2micaps(config_file):
    """
DESCRIPTION
    Convert GrADS binary data file to MICAPS class 4 data file according to a config file.
"""
    porter_tool = Porter()
    for config_file in config_file:
        porter_tool.convert(config_file)


if __name__ == "__main__":
    cli()
