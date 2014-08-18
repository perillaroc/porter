"""
porter: a tool for GrADS data converting
"""
import getopt
import sys
import os
import json
import datetime
from grads2micaps import Grads2Micaps
from ctlparser import GradsCtlParser, GradsCtl


class Porter:
    def __init__(self):
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
                    print "parser start_time error: %s" % start_time_str

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
                convert_type = a_record["type"]
                if convert_type == "micaps.4":
                    grads_to_micaps = Grads2Micaps(grads_ctl)
                    a_record['output_dir'] = output_dir
                    grads_to_micaps.convert(a_record)
                else:
                    print "Not implemented for %s" % convert_type


if __name__ == "__main__":

    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) < 1:
        print """Usage: %s config_file
        """ % os.path.basename(sys.argv[0])
        sys.exit()

    porter_tool = Porter()
    porter_tool.convert(args[0])
