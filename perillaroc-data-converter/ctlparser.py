"""
ctl parser
"""

import datetime


class GradsCtl:

    content = dict()

    def __init__(self):
        self.content['options'] = list()

    def __str__(self):
        return "a GradsCtl object with content:\n%s" % self.content


class GradsCtlParser:

    grads_ctl = GradsCtl()
    ctl_file_lines = list()
    cur_no = -1

    def __init__(self):
        pass

    def dset_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        dset = cur_line[4:].strip()
        self.grads_ctl.content['dset'] = dset

    def options_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        options = cur_line[7:].strip().split(' ')
        self.grads_ctl.content['options'].append(options)

    def title_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        title = cur_line[5:].strip()
        self.grads_ctl.content['title'] = title

    def undef_parser(self):
        cur_line = self.ctl_file_lines[self.cur_no]
        undef = cur_line[5:].strip()
        self.grads_ctl.content['undef'] = float(undef)

    def dimension_parser(self):
        """
        parser for xdef, ydef and zdef
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
            #levels = [start+step*n for n in range(count)]
            self.grads_ctl.content[parser_type] = {
                'type': 'linear',
                'count': count,
                'start': start,
                'step': step,
                #'values': levels
            }
            pass
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

            self.grads_ctl.content[parser_type] = {
                'type': 'levels',
                'count': count,
                'values': levels
            }
            pass

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

        self.grads_ctl.content['tdef'] = {
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

        self.grads_ctl.content['vars'] = varlist

    parser_mapper = {
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
        with open(ctl_file_path) as f:
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

if __name__ == "__main__":
    import getopt
    import sys
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