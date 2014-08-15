"""
GrADS data to micaps data conventer.
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

    def __init__(self):
        pass

    def convert_record(self, name, level='.single.', time_index=0, output_dir="."):
        """
        convert a record with name, level and time index in GrADS data file.
        """
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

            output_file_name = self.grads_ctl.tdef['start'].strftime("%Y%m%d%H")
            output_file_dir = output_dir + os.sep + name + "_4"
            if not level == '.single.':
                output_file_dir += os.sep + str(int(level))
                a_level = level
            else:
                a_level = 0

            if not os.path.isdir(output_file_dir):
                os.makedirs(output_file_dir)
            os.chdir(output_file_dir)

            with open(output_file_name, 'w') as output_file:
                output_file.write("diamond ")
                output_file.write("4 ")
                output_file.write("comment \n")
                output_file.write(str(self.grads_ctl.start_time.year)[-2:] + " ")
                output_file.write("%02d " % self.grads_ctl.start_time.month)
                output_file.write("%02d " % self.grads_ctl.start_time.day)
                output_file.write("%02d " % self.grads_ctl.start_time.hour)
                output_file.write("%03d " % self.grads_ctl.forecast_hour)
                output_file.write("%d " % a_level)
                output_file.write("%f " % x_count)
                output_file.write("%f " % y_count)
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][-1])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][-1])
                output_file.write("%d " % self.grads_ctl.xdef['count'])
                output_file.write("%d " % self.grads_ctl.ydef['count'])
                output_file.write("%.2f " % 4.00)
                output_file.write("%.2f " % min(var_list))
                output_file.write("%.2f " % max(var_list))
                output_file.write("%d " % 2)
                output_file.write("%.2f " % 0.00)
                output_file.write("\n")

                var_list_str = ["%.2f" % (a_var-273.16) for a_var in var_list]
                output_file.write(" ".join(var_list_str))

    def convert(self, ctl_file_path, output_dir):
        self.grads_ctl_parser.parse(ctl_file_path)
        self.convert_record("t", 850.0, output_dir=output_dir)

if __name__ == "__main__":
    import getopt
    import sys
    import os
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) < 2:
        print """Usage: %s ctl_file_path output_dir
        """ % os.path.basename(sys.argv[0])
        sys.exit()

    grads_2_micaps = Grads2Micaps()
    grads_2_micaps.convert(args[0], args[1])
