"""
Parse GrADS binary data file with a ctl file.
"""


from ctlparser import GradsCtl


class GradsDataParser(object):

    def __init__(self):
        self._grads_ctl = GradsCtl()
        self.local_endian = sys.byteorder
        self.data_endian = ''
        self.sequential = 0

    @property
    def grads_ctl(self):
        return self._grads_ctl

    @grads_ctl.setter
    def grads_ctl(self, a_grads_ctl):
        self._grads_ctl = a_grads_ctl
        if 'big_endian' in self.grads_ctl.options:
            self.data_endian = 'big'
        else:
            self.data_endian = 'little'

        if 'sequential' in self.grads_ctl.options:
            self.sequential = 1

    def get_offset_by_index(self, var_index, level_index=0, time_index=0):
        offset = 0

        # check params
        if time_index:
            raise Exception("time_index more than 0 is not supported")
        if grads_ctl.vars[var_index]['levels'] <= level_index:
            raise Exception("level index is too large.")

        # calculate record index
        pos = 0
        for a_var_index in range(0, var_index):
            levels = grads_ctl.vars[a_var_index]['levels']
            if levels == 0:
                pos += 1
            else:
                pos += levels

        # calculate offset
        nx = grads_ctl.xdef['count']
        ny = grads_ctl.ydef['count']
        if self.sequential == 1:
            offset += (nx*ny*4+2*4)*(pos+level_index)
        else:
            offset += nx*ny*4*(pos+level_index)

        return offset

if __name__ == "__main__":
    import getopt
    import sys
    import struct
    from ctlparser import GradsCtlParser
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) == 0:
        print """
        Usage: %s ctl_file_path
        """ % sys.argv[0]
        sys.exit()

    file_path = args[0]
    grads_ctl_parser = GradsCtlParser()
    grads_ctl_parser.parse(file_path)
    grads_data_parser = GradsDataParser()
    grads_ctl = grads_ctl_parser.grads_ctl
    grads_data_parser.grads_ctl = grads_ctl

    # open data file
    ycount = grads_ctl.ydef['count']
    xcount = grads_ctl.xdef['count']
    print "length of the record: %d " % (xcount * ycount * 4)
    data_file = open(grads_ctl.dset, 'rb')
    data_file.seek(grads_data_parser.get_offset_by_index(0, 0))
    record_length_str = data_file.read(4)
    record_length = struct.unpack('>I', record_length_str)[0]
    print "length written at the beginning of the record: %d " % record_length

    var_list = [struct.unpack('>f', data_file.read(4))[0] for i in range(0, ycount*xcount)]

    record_length_str = data_file.read(4)
    record_length = struct.unpack('>I', record_length_str)[0]
    print "length written at the end of the record: %d " % record_length

    print "min value: %f" % min(var_list)
    print "max value: %f" % max(var_list)