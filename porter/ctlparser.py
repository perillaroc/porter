"""
ctl parser
"""

import datetime
import os
import sys
import re


class GradsCtl:
    __content = dict()

    def __init__(self):
        self.__content['options'] = list()
        self.data_endian = 'little'
        self.local_endian = sys.byteorder
        self.yrev = 0

    def __str__(self):
        return "<GradsCtl>\n%s" % self.__content

    def __setattr__(self, key, value):
        self.__content[key] = value

    def __getattr__(self, item):
        if item in self.__content:
            return self.__content[item]
        else:
            raise AttributeError(item)

    def __delattr__(self, item):
        del self.__content[item]


class GradsCtlParser:

    def __init__(self, grads_ctl=GradsCtl()):
        self.ctl_file_path = ''

        self.grads_ctl = grads_ctl
        self.ctl_file_lines = list()
        self.cur_no = -1

    def ctl_file_name_parser(self):
        ctl_file_name = os.path.basename(self.ctl_file_path)

        if hasattr(self.grads_ctl, 'start_time') \
                and hasattr(self.grads_ctl, 'forecast_time'):
            pass
        else:
            print "guess start time and forecast time"

            if ctl_file_name.startswith("post.ctl_"):
                # check for grapes meso v4.0 which format is:
                #   post.ctl_201408111202900
                if re.match(r"post.ctl_[0-9]{15}", ctl_file_name):
                    self.grads_ctl.start_time = datetime.datetime.strptime(ctl_file_name[9:19], "%Y%m%d%H")
                    self.grads_ctl.forecast_time = datetime.timedelta(hours=int(ctl_file_name[19:22]))
                # check for grapes gfs which format is
                #   post.ctl_2014081112_001
                elif re.match(r"post.ctl_[0-9]{10}_[0-9]{3}", ctl_file_name):
                    self.grads_ctl.start_time = datetime.datetime.strptime(ctl_file_name[9:19], "%Y%m%d%H")
                    self.grads_ctl.forecast_time = datetime.timedelta(hours=int(ctl_file_name[21:24]))
                else:
                    # TODO (windroc, 2014.08.18): other file type
                    print "We can't recognize ctl file name. You're better to set start time and forecast time" \
                          " in the config file."

    def dset_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        dset = cur_line[4:].strip()
        if dset[0] == '^':
            (filepath, filename) = os.path.split(self.ctl_file_path)
            dset = os.path.join(filepath, dset[1:])

        self.grads_ctl.dset = dset

    def options_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        options = cur_line[7:].strip().split(' ')
        self.grads_ctl.options.extend(options)
        for an_option in options:
            if an_option == 'big_endian':
                self.grads_ctl.data_endian = 'big'
            elif an_option == 'little_endian':
                self.grads_ctl.data_endian = 'little'
            elif an_option == 'yrev':
                self.grads_ctl.yrev = True

    def title_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        title = cur_line[5:].strip()
        self.grads_ctl.title = title

    def undef_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        undef = cur_line[5:].strip()
        self.grads_ctl.undef = float(undef)

    def dimension_parser(self):
        """
        parser for keywords xdef, ydef and zdef
        """
        cur_line = self.ctl_file_lines[self.cur_no].lower()
        parts = cur_line.split()
        parser_type = parts[0]
        count = int(parts[1])
        if parts[2] == 'linear':
            # x use linear mapping
            if len(parts) < 4:
                raise Exception("%s parser error" % parser_type)
            start = float(parts[3])
            step = float(parts[4])
            levels = [start+step*n for n in range(count)]
            setattr(self.grads_ctl, parser_type, {
                'type': 'linear',
                'count': count,
                'start': start,
                'step': step,
                'values': levels
            })
        elif parts[2] == 'levels':
            # x user explicit levels
            levels = list()
            if len(parts) > 2:
                levels = [float(l) for l in parts[3:]]
            i = len(levels)
            while i < count:
                self.cur_no += 1
                cur_line = self.ctl_file_lines[self.cur_no]
                levels.append(float(cur_line))
                i += 1

            setattr(self.grads_ctl, parser_type, {
                'type': 'levels',
                'count': count,
                'values': levels
            })

    def tdef_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        parts = cur_line.strip().split()
        assert parts[2] == "linear"
        assert len(parts) == 5
        count = int(parts[1])

        # parse start time
        # format:
        #     hh:mmZddmmmyyyy
        # where:
        #     hh	=	hour (two digit integer)
        #     mm	=	minute (two digit integer)
        #     dd	=	day (one or two digit integer)
        #     mmm	=	3-character month
        #     yyyy	=	year (may be a two or four digit integer;
        #                       2 digits implies a year between 1950 and 2049)
        start_string = parts[3]
        start_date = datetime.datetime.now()
        if start_string[3] == ':':
            raise Exception('Not supported time with hh')
            pass
        elif len(start_string) == 12:
            start_date = datetime.datetime.strptime(start_string.lower(), '%Hz%d%b%Y')

        # parse increment time
        # format:
        #     vvkk
        # where:
        #     vv	=	an integer number, 1 or 2 digits
        #     kk	=	mn (minute)
        #             hr (hour)
        #             dy (day)
        #             mo (month)
        #             yr (year)
        increment_string = parts[4]
        vv = int(increment_string[:-2])
        kk = increment_string[-2:]
        time_step = datetime.timedelta()
        if kk == 'mn':
            time_step = datetime.timedelta(minutes=vv)
        elif kk == 'hr':
            time_step = datetime.timedelta(hours=vv)
        elif kk == 'dy':
            time_step = datetime.timedelta(days=vv)
        elif kk == 'mo':
            raise Exception("month is not supported")
        elif kk == 'year':
            raise Exception("year is not supported")

        values = [start_date + time_step * i for i in range(count)]

        self.grads_ctl.tdef = {
            'type': 'linear',
            'count': count,
            'start': start_date,
            'step': time_step,
            'values': values
        }

    def vars_parser(self):
        varlist = list()

        parts = self.ctl_file_lines[self.cur_no].strip().split()
        assert len(parts) == 2
        count = int(parts[1])
        for i in range(count):
            # parse one var line
            self.cur_no += 1
            cur_line = self.ctl_file_lines[self.cur_no].strip()
            parts = cur_line.split()
            # we currently use old style of var record.
            # TODO: check for new type of record from GrADS v2.0.2

            var_name = parts[0]
            levels = int(parts[1])
            units = parts[2]
            description = " ".join(parts[3:])

            cur_var = {
                'name': var_name,
                'levels': levels,
                'units': units,
                'description': description
            }
            varlist.append(cur_var)

        self.grads_ctl.vars = varlist

        # generate record list
        record_list = list()
        for a_var_record in varlist:
            if a_var_record['levels'] == 0:
                record_list.append({
                    'name': a_var_record['name'],
                    'level_type': 'single',
                    'level': 0,
                    'level_index': 0,
                    'units': a_var_record['units'],
                    'description': a_var_record['description']
                })
            else:
                for level_index in range(0, a_var_record["levels"]):
                    a_level = self.grads_ctl.zdef["values"][level_index]
                    record_list.append({
                        'name': a_var_record['name'],
                        'level_type': 'multi',
                        'level': a_level,
                        'level_index': level_index,
                        'units': a_var_record['units'],
                        'description': a_var_record['description']
                    })

        self.grads_ctl.record = record_list

    parser_mapper = {
        'ctl_file_name': ctl_file_name_parser,
        'dset': dset_parser,
        'options': options_parser,
        'title': title_parser,
        'undef': undef_parser,
        'xdef': dimension_parser,
        'ydef': dimension_parser,
        'zdef': dimension_parser,
        'tdef': tdef_parser,
        'vars': vars_parser,
    }

    def parse(self, ctl_file_path):
        self.ctl_file_path = os.path.abspath(ctl_file_path)
        with open(ctl_file_path) as f:
            self.ctl_file_name_parser()

            lines = f.readlines()
            self.ctl_file_lines = [l.strip() for l in lines]
            self.cur_no = 0
            total_lines = len(lines)
            while self.cur_no < total_lines:
                cur_line = lines[self.cur_no]
                first_word = cur_line[0:cur_line.find(' ')]
                if first_word.lower() in self.parser_mapper:
                    self.parser_mapper[first_word](self)
                self.cur_no += 1
        return self.grads_ctl

if __name__ == "__main__":
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) == 0:
        print """
        Usage: %s ctl_file_path
        """ % sys.argv[0]
        sys.exit()

    file_path = args[0]
    grads_ctl_parser = GradsCtlParser()
    grads_ctl_parser.parse(file_path)
    print grads_ctl_parser.grads_ctl