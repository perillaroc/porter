# coding: utf-8
"""
Parse GrADS binary data file with a ctl file.
"""

from __future__ import print_function, absolute_import

from porter.grads_parser.grads_ctl_parser import GradsCtl


class GradsDataParser(object):
    __grads_ctl = GradsCtl()

    def __init__(self, a_grads_ctl=GradsCtl()):
        self.grads_ctl = a_grads_ctl

    @property
    def grads_ctl(self):
        return self.__grads_ctl

    @grads_ctl.setter
    def grads_ctl(self, a_grads_ctl):
        self.__grads_ctl = a_grads_ctl

    def get_record_offset_by_record_index(self, record_index):
        offset = 0
        nx = self.grads_ctl.xdef['count']
        ny = self.grads_ctl.ydef['count']
        if 'sequential' in self.grads_ctl.options:
            offset += (nx*ny*4+2*4)*record_index
        else:
            offset += nx*ny*4*record_index

        return offset

    def get_record_offset(self, var_index, level_index=0, time_index=0):
        # check params
        if time_index:
            raise Exception("time_index more than 0 is not supported")
        var_levels = self.grads_ctl.vars[var_index]['levels']
        if 0 < var_levels <= level_index:
            raise Exception("level index is too large.")

        # calculate record index
        pos = 0
        for a_var_index in range(0, var_index):
            levels = self.grads_ctl.vars[a_var_index]['levels']
            if levels == 0:
                pos += 1
            else:
                pos += levels

        pos += level_index

        print("var name: %s" % grads_ctl.vars[var_index]['name'])
        if grads_ctl.vars[var_index]['levels'] == 0:
            print("var level: single")
        else:
            print("var level: %f" % grads_ctl.zdef['values'][level_index])
        print("pos:%d" % pos)

        # calculate offset
        return self.get_record_offset_by_record_index(pos)

    def get_record_index(self, name, level=0, level_type='multi', var_time_index=0):
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
            return cur_i
        else:
            return -1


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
    grads_ctl_parser = GradsCtlParser()
    grads_ctl_parser.parse(file_path)
    grads_data_parser = GradsDataParser()
    grads_ctl = grads_ctl_parser.grads_ctl
    grads_data_parser.grads_ctl = grads_ctl

    # open data file
    y_count = grads_ctl.ydef['count']
    x_count = grads_ctl.xdef['count']
    print("length of the record: %d " % (x_count * y_count * 4))
    data_file = open(grads_ctl.dset, 'rb')
    data_file.seek(grads_data_parser.get_record_offset(2, 5))
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

    record_index = grads_data_parser.get_record_index('t', 850)
    print(record_index)
