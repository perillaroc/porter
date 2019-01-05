# coding: utf-8

from __future__ import print_function, absolute_import

from porter.grads_parser.grads_ctl_parser import GradsCtl
from porter.grads_parser.grads_record_handler import GradsRecordHandler


class GradsDataHandler(object):
    """
    Parse GrADS binary data file with a ctl file.
    """
    def __init__(self, a_grads_ctl=None):
        if a_grads_ctl is None:
            a_grads_ctl = GradsCtl()

        self.grads_ctl = a_grads_ctl

    def get_offset_by_record_index(self, record_index):
        """
        get offset by record index

        :param record_index: record index
        :return: record offset
        """
        if record_index >= len(self.grads_ctl.record):
            raise ValueError('record_index is too large.')

        offset = 0
        nx = self.grads_ctl.xdef['count']
        ny = self.grads_ctl.ydef['count']
        if 'sequential' in self.grads_ctl.options:
            offset += (nx * ny + 2) * 4 * record_index
        else:
            offset += nx * ny * 4 * record_index

        return offset

    def get_offset_by_index(self, var_index, level_index=0):
        """
        get record offset by variable and level index.

        :param var_index:
        :param level_index:
        :return: record offset
        """

        record = self.get_record_by_index(var_index, level_index)
        return record.offset

    def find_record(self, name, level=0, level_type='multi'):
        """
        find record index by field name, level value, level type.

        :param name: field name, found name in vars section of ctl files.
        :param level: level value
        :param level_type: multi or single
        :return: GradsRecordHandler or None
        """
        cur_i = 0
        if level_type == 'single':
            a_level = 0
        else:
            a_level = float(level)

        while cur_i < len(self.grads_ctl.record):
            cur_record = self.grads_ctl.record[cur_i]
            if cur_record['name'] == name \
                    and cur_record['level_type'] == level_type \
                    and cur_record['level'] == a_level:
                break
            cur_i += 1
        if cur_i < len(self.grads_ctl.record):
            offset = self.get_offset_by_record_index(cur_i)
            record = GradsRecordHandler(self.grads_ctl, cur_i, offset)
            return record
        else:
            return None

    def get_record_by_index(self, var_index, level_index=0):
        """
        get record from variable and level index.

        :param var_index:
        :param level_index:
        :return: GradsRecordHandler
        """
        if var_index >= len(self.grads_ctl.vars):
            raise ValueError("variable index is too large.")

        var_levels = self.grads_ctl.vars[var_index]['levels']
        if 0 < var_levels <= level_index:
            raise ValueError("level index is too large.")

        # calculate record index
        pos = 0
        for a_var_index in range(0, var_index):
            levels = self.grads_ctl.vars[a_var_index]['levels']
            if levels == 0:
                pos += 1
            else:
                pos += levels

        pos += level_index

        offset = self.get_offset_by_record_index(pos)

        record = GradsRecordHandler(self.grads_ctl, pos, offset, var_index=var_index, level_index=level_index)
        return record


if __name__ == "__main__":
    import getopt
    import sys
    import struct
    from porter.grads_parser.grads_ctl_parser import GradsCtlParser
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) == 0:
        print("""
        Usage: %s ctl_file_path
        """ % sys.argv[0])
        sys.exit()

    file_path = args[0]
    ctl_parser = GradsCtlParser()
    ctl_parser.parse(file_path)
    data_handler = GradsDataHandler()
    grads_ctl = ctl_parser.grads_ctl
    data_handler.grads_ctl = grads_ctl

    # open data file
    y_count = grads_ctl.ydef['count']
    x_count = grads_ctl.xdef['count']
    print("length of the record: %d " % (x_count * y_count * 4))
    data_file = open(grads_ctl.dset, 'rb')
    data_file.seek(data_handler.get_offset_by_index(2, 5))
    record_length_str = data_file.read(4)
    record_length = struct.unpack('>I', record_length_str)[0]
    print("length written at the beginning of the record: %d " % record_length)

    var_list = [struct.unpack('>f', data_file.read(4))[0] for i in range(0, y_count*x_count)]

    record_length_str = data_file.read(4)
    record_length = struct.unpack('>I', record_length_str)[0]
    print("length written at the end of the record: %d " % record_length)

    print("min value: %f" % min(var_list))
    print("max value: %f" % max(var_list))

    print("first ten values in record:")
    print([a-273.16 for a in var_list[0:100]])

    print("Test for get record index:")

    record_index = data_handler.find_record('t', 850)
    print(record_index)
