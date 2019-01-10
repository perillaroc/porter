# coding: utf-8
import numpy as np


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
            # print("Data endian is not found. Use local endian to unpack values.")
            data_format = 'f'

        # load data from file
        data_file.seek(self.offset)

        var_yrev = self.grads_ctl.yrev

        values = np.fromfile(data_file, dtype=np.dtype(data_format), count=x_count * y_count)
        values = values.reshape((y_count, x_count))

        if var_yrev:
            values = np.flip(values, 0)

        self.data = values
