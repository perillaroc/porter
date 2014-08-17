"""
GrADS data to micaps data converter.
"""

from ctlparser import GradsCtl
from ctlparser import GradsCtlParser
from gradsdataparser import GradsDataParser
import struct
import os


class Grads2Micaps:
    """
    Convert GrADS data to micaps data
    """
    grads_ctl = GradsCtl()
    grads_ctl_parser = GradsCtlParser(grads_ctl)
    grads_data_parser = GradsDataParser(grads_ctl)

    def __init__(self, a_grads_ctl=GradsCtl()):
        self.grads_ctl = a_grads_ctl

    def set_grads_ctl_path(self, ctl_path):
        self.grads_ctl_parser.parse(ctl_path)

    def convert(self, a_config_record):
        a_name = a_config_record['name']
        a_level = a_config_record.get('level', '.single.')
        an_output_dir = a_config_record.get('output_dir', '.')
        a_time_index = a_config_record.get('time_index', 0)
        a_value_func = eval("lambda x: "+a_config_record.get('value', 'x'))

        self.convert_record(a_name,
                            a_level,
                            a_time_index,
                            an_output_dir,
                            a_value_func)

    def convert_record(self, name, level='.single.', time_index=0, output_dir=".",
                       value_func=lambda x: x):
        """
        convert a record with name, level and time index in GrADS data file.
        """
        output_file_name = self.grads_ctl.tdef['start'].strftime("%Y%m%d%H")
        output_file_dir = output_dir + os.sep + name + "_4"
        if not level == '.single.':
            output_file_dir += os.sep + str(int(level))
            a_level = float(level)
        else:
            a_level = 0
        record_index = self.grads_data_parser.get_record_index(name, level, time_index)
        offset = self.grads_data_parser.get_record_offset_by_record_index(record_index)

        with open(self.grads_ctl.dset, 'rb') as data_file:
            data_file.seek(offset + 4)
            x_count = self.grads_ctl.xdef['count']
            y_count = self.grads_ctl.ydef['count']

            if self.grads_ctl.data_endian == 'big':
                data_format = '>f'
            else:
                data_format = '<f'

            var_list = [struct.unpack(data_format, data_file.read(4))[0] for i in range(0, y_count*x_count)]

            if not os.path.isdir(output_file_dir):
                os.makedirs(output_file_dir)

            with open(output_file_dir + os.sep + output_file_name, 'w') as output_file:
                output_file.write("diamond ")
                output_file.write("4 ")
                output_file.write("comment \n")
                output_file.write(str(self.grads_ctl.start_time.year)[-2:] + " ")
                output_file.write("%02d " % self.grads_ctl.start_time.month)
                output_file.write("%02d " % self.grads_ctl.start_time.day)
                output_file.write("%02d " % self.grads_ctl.start_time.hour)
                output_file.write("%03d " % self.grads_ctl.forecast_hour)
                output_file.write("%d " % a_level)
                output_file.write("%.2f " % self.grads_ctl.xdef['step'])
                output_file.write("%.2f " % self.grads_ctl.ydef['step'])
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][-1])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][-1])
                output_file.write("%d " % x_count)
                output_file.write("%d " % y_count)
                output_file.write("%.2f " % 4.00)
                output_file.write("%.2f " % value_func(min(var_list)))
                output_file.write("%.2f " % value_func(max(var_list)))
                output_file.write("%d " % 2)
                output_file.write("%.2f " % 0.00)
                output_file.write("\n")

                var_list_str = ["%.2f" % (value_func(a_var)) for a_var in var_list]
                output_file.write(" ".join(var_list_str))


if __name__ == "__main__":
    import getopt
    import sys
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) < 2:
        print """Usage: %s ctl_file_path output_dir
        """ % os.path.basename(sys.argv[0])
        sys.exit()

    grads_2_micaps = Grads2Micaps()
    grads_2_micaps.set_grads_ctl_path(args[0])
    grads_2_micaps.convert_record("t", 850.0, output_dir=args[1], value_func=lambda x: x-273.16)
