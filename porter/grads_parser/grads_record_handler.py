# coding: utf-8
import struct
import sys


class GradsRecordHandler(object):
    def __init__(self, grads_ctl, record_index, offset, var_index=-1, level_index=-1):
        self.grads_ctl = grads_ctl
        self.record_index = record_index
        self.record_info = grads_ctl.record[record_index]
        self.offset = offset

        self.var_index = var_index
        self.level_index = level_index

        self.data = None

    def load_data(self, data_file):
        if 'sequential' in self.grads_ctl.options:
            self.offset += 4
        x_count = self.grads_ctl.xdef['count']
        y_count = self.grads_ctl.ydef['count']

        if self.grads_ctl.data_endian == 'big':
            data_format = '>f'
        elif self.grads_ctl.data_endian == 'little':
            data_format = '<f'
        else:
            print("Data endian is not found. Use local endian to unpack values.")
            if sys.byteorder == "big":
                data_format = '>f'
            else:
                data_format = '<f'

        # load data from file
        data_file.seek(self.offset)

        if hasattr(self.grads_ctl, "yrev") and self.grads_ctl.yrev is True:
            var_yrev = True
        else:
            var_yrev = False

        var_list = [struct.unpack(data_format, data_file.read(4))[0] for i in range(0, y_count * x_count)]

        # process yrev
        if var_yrev:
            new_var_list = list()
            for i in range(0, y_count):
                new_var_list.extend(var_list[(y_count - 1 - i) * x_count:(y_count - i) * x_count])
            del var_list
            var_list = new_var_list

        self.data = var_list
