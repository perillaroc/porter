"""
ctl parser
"""

import datetime

grads_ctl = dict()
grads_ctl['options'] = list()

def dset_parser(ctl_file_lines, cur_no):
    cur_line = ctl_file_lines[cur_no]
    dset = cur_line[4:].strip()
    grads_ctl['dset'] = dset
    return cur_no


def options_parser(ctl_file_lines, cur_no):
    cur_line = ctl_file_lines[cur_no]
    options = cur_line[7:].strip().split(' ')
    grads_ctl['options'].append(options)
    return cur_no


def title_parser(ctl_file_lines, cur_no):
    cur_line = ctl_file_lines[cur_no]
    title = cur_line[5:].strip()
    grads_ctl['title'] = title
    return cur_no


def undef_parser(ctl_file_lines, cur_no):
    cur_line = ctl_file_lines[cur_no]
    undef = cur_line[5:].strip()
    grads_ctl['undef'] = float(undef)
    return cur_no


def dimension_parser(ctl_file_lines, cur_no):
    """
    parser for xdef, ydef and zdef
    """
    cur_line = ctl_file_lines[cur_no].lower()
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
        grads_ctl[parser_type] = {
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
            cur_no += 1
            cur_line = ctl_file_lines[cur_no]
            levels.append(float(cur_line))
            i += 1

        grads_ctl[parser_type] = {
            'type': 'levels',
            'count': count,
            'values': levels
        }
        pass

    return cur_no


def tdef_parser(ctl_file_lines, cur_no):
    cur_line = ctl_file_lines[cur_no]
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

    grads_ctl['tdef'] = {
        'type': 'linear',
        'count': count,
        'start': start_date,
        'step': time_step,
        'values': values
    }

    return cur_no


def vars_parser(ctl_file_lines, cur_no):
    varlist = list()

    parts = ctl_file_lines[cur_no].strip().split()
    assert len(parts) == 2
    count = int(parts[1])
    for i in range(count):
        # parse one var line
        cur_no += 1
        cur_line = ctl_file_lines[cur_no].strip()
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

    grads_ctl['vars'] = varlist
    return cur_no


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


def parse_ctl_file(ctl_file):
    with open(ctl_file) as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        i = 0
        total_lines = len(lines)
        while i < total_lines:
            cur_line = lines[i]
            first_word = cur_line[0:cur_line.find(' ')]
            if first_word.lower() in parser_mapper:
                i = parser_mapper[first_word](
                    ctl_file_lines=lines,
                    cur_no=i
                )
            i += 1


if __name__ == "__main__":
    import getopt
    import sys
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) == 0:
        print """
        Usage: %s ctl_file_path
        """ % sys.argv[0]
        sys.exit()

    ctl_file_path = args[0]
    parse_ctl_file(ctl_file_path)
    print grads_ctl