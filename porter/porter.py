"""
porter: a tool for GrADS data converting
"""
import getopt
import sys
import os
import json
from grads2micaps import Grads2Micaps
from ctlparser import GradsCtlParser


class Porter:
    def __init__(self):
        pass

    def convert(self, config_file_path):
        with open(config_file_path) as config_file:
            config_str = config_file.read()
            config_object = json.loads(config_str, encoding='utf-8')

            ctl_file_path = os.path.abspath(config_object['ctl'])
            output_dir = os.path.abspath(config_object['output_dir'])
            records = config_object['records']

            # ctl parser
            grads_ctl_parser = GradsCtlParser()
            grads_ctl = grads_ctl_parser.parse(ctl_file_path)

            # output parser

            # record parser
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
