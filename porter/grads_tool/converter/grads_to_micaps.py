# coding: utf-8
"""
GrADS data to micaps data converter.
"""
from __future__ import print_function, absolute_import
import os

import numpy as np

from porter.grads_parser.grads_ctl_parser import GradsCtl, GradsCtlParser
from porter.grads_parser.grads_data_handler import GradsDataHandler


class GradsToMicaps(object):
    """
    Convert GrADS data to micaps data
    """

    def __init__(self, grads_ctl=GradsCtl()):
        self.grads_ctl = grads_ctl
        self.grads_ctl_parser = GradsCtlParser(grads_ctl)
        self.grads_data_parser = GradsDataHandler(grads_ctl)

    def set_grads_ctl_path(self, ctl_path):
        self.grads_ctl_parser.parse(ctl_path)

    def convert(self, a_config_record):
        a_name = a_config_record['name']
        a_level = a_config_record.get('level', '0')
        a_level_type = a_config_record.get('level_type', 'multi')
        an_output_dir = a_config_record.get('output_dir', '.')
        a_time_index = a_config_record.get('time_index', 0)
        a_value_func = eval("lambda x: "+a_config_record.get('value', 'x'))
        record_target_type = a_config_record.get('target_type','')

        if record_target_type == "micaps.4":
            self.convert_record_to_type_4(a_name,
                                          a_level,
                                          a_level_type,
                                          a_time_index,
                                          an_output_dir,
                                          a_value_func)
        else:
            print("TYPE: {record_target_type} has not implemented!".format(record_target_type=record_target_type))

    def convert_record_to_type_4(self, name,
                                 level=0.0,
                                 level_type='multi',
                                 time_index=0,
                                 output_dir=".",
                                 value_func=lambda x: x):
        """
        convert a record with name, level and time index in GrADS data file.

        """

        micaps_data_type = "4"

        a_forecast_hour = self.grads_ctl.forecast_time.seconds / 3600
        comment = name + '_'+self.grads_ctl.start_time.strftime("%Y%m%d%H") + "_%03d" % a_forecast_hour

        output_file_name = self.grads_ctl.start_time.strftime("%Y%m%d%H") + ".%03d" % a_forecast_hour
        output_file_dir = output_dir + os.sep + name + "_" + micaps_data_type
        if not level_type == 'single':
            output_file_dir += os.sep + str(int(level))
            a_level = float(level)
        else:
            a_level = 0

        record = self.grads_data_parser.find_record(name, level, level_type)

        with open(self.grads_ctl.dset, 'rb') as data_file:
            record.load_data(data_file)
            var_list = record.data.ravel()

            vfunc = np.vectorize(value_func)
            var_list = vfunc(var_list)

            from porter.micaps_writer.micaps_type_4_writer import MicapsType4Data, MicapsType4Writer

            micaps_data = MicapsType4Data()
            micaps_data.comment = comment
            micaps_data.start_time = self.grads_ctl.start_time
            micaps_data.forecast_hour = a_forecast_hour
            micaps_data.level = a_level
            micaps_data.x_step = self.grads_ctl.xdef['step']
            micaps_data.y_step = self.grads_ctl.ydef['step']
            micaps_data.x_start_value = self.grads_ctl.xdef['values'][0]
            micaps_data.x_end_value = self.grads_ctl.xdef['values'][-1]
            micaps_data.y_start_value = self.grads_ctl.ydef['values'][0]
            micaps_data.y_end_value = self.grads_ctl.ydef['values'][-1]
            micaps_data.x_count = self.grads_ctl.xdef['count']
            micaps_data.y_count = self.grads_ctl.ydef['count']
            micaps_data.contour_step = 4.00
            micaps_data.contour_start_value = min(var_list)
            micaps_data.contour_end_value = max(var_list)
            micaps_data.smooth = 2
            micaps_data.bold_value = 0.00
            micaps_data.values = var_list

            MicapsType4Writer.write_to_file(micaps_data, output_file_dir + os.sep + output_file_name)


if __name__ == "__main__":
    import getopt
    import sys
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) < 2:
        print("""Usage: %s ctl_file_path output_dir
        """ % os.path.basename(sys.argv[0]))
        sys.exit()

    grads_2_micaps = GradsToMicaps()
    grads_2_micaps.set_grads_ctl_path(args[0])
    grads_2_micaps.convert_record_to_type_4("t", level=850.0, output_dir=args[1], value_func=lambda x: x-273.16)
