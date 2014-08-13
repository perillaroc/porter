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
        if 'big_endian' in self.grads_ctl.content['options']:
            self.data_endian = 'big'
        else:
            self.data_endian = 'little'

        if 'sequential' in self.grads_ctl.content['options']:
            self.sequential = 1

    def get_offset_by_index(self, var_index, level_index=0, time_index=0):
        # check params
        if time_index:
            raise Exception("time_index more than 0 is not supported")
        ctl_content = self.grads_ctl.content
        if ctl_content[var_index]['levels']['count'] <= level_index:
            raise Exception("level index is too large.")

        # calculate record index
        offset = 0
        pos = 0
        for i in range(0, var_index):
            levels = ctl_content['vars'][i]['levels']
            if levels == 0:
                pos += 1
            else:
                pos += levels

        # calculate offset
        nx = ctl_content['xdef']['count']
        ny = ctl_content['ydef']['count']
        if self.sequential == 1:
            offset += (nx*ny*4+2*4)*(pos+level_index)
        else:
            offset += nx*ny*4*(pos+level_index)

        return offset

if __name__ == "__main__":
    import getopt
    import sys
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
    grads_data_parser.grads_ctl = grads_ctl_parser.grads_ctl

    print grads_data_parser.get_offset_by_index(1, 1)
