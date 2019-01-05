# coding=utf-8
from datetime import datetime, timedelta
from pytest import approx

from porter.grads_parser.grads_ctl_parser import GradsCtlParser
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class TestGradsCtlParser(object):
    def test_ctl_file_name_parser(self):
        parser = GradsCtlParser()
        parser.ctl_file_path = str(Path(__file__, 'post.ctl_2018011912_000'))
        parser.parse_ctl_file_name()
        assert parser.grads_ctl.start_time == datetime(2018, 1, 19, 12)
        assert parser.grads_ctl.forecast_time == timedelta(hours=0)

        parser = GradsCtlParser()
        parser.ctl_file_path = str(Path(__file__, 'post.ctl_201801191200300'))
        parser.parse_ctl_file_name()
        assert parser.grads_ctl.start_time == datetime(2018, 1, 19, 12)
        assert parser.grads_ctl.forecast_time == timedelta(hours=3)

    def test_dset_parser(self):
        ctl_content = """dset ^postvar2018011912_000"""
        parser = GradsCtlParser()
        parser.ctl_file_path = str(Path(__file__, 'post.ctl_2018011912_000'))
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_dset()

        assert parser.grads_ctl.dset == str(Path(__file__, 'postvar2018011912_000'))

    def test_options_parser(self):
        ctl_content = """options big_endian"""
        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_options()
        assert parser.grads_ctl.data_endian == 'big'
        assert parser.grads_ctl.options[0] == 'big_endian'

        ctl_content = """options little_endian"""
        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_options()
        assert parser.grads_ctl.options[0] == 'little_endian'

        ctl_content = """options little_endian yrev"""
        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_options()
        assert parser.grads_ctl.data_endian == 'little'
        assert parser.grads_ctl.options[0] == 'little_endian'
        assert parser.grads_ctl.yrev
        assert parser.grads_ctl.options[1] == 'yrev'

    def test_title_parser(self):
        ctl_content = """title post output from grapes"""

        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_title()
        assert parser.grads_ctl.title == 'post output from grapes'

    def test_undef_parser(self):
        ctl_content = """undef -9999."""

        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_undef()
        assert parser.grads_ctl.undef == approx(-9999.0)

    def test_linear_dimension_parser(self):
        ctl_content = """xdef 1440 linear    0.0000    0.2500"""

        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_dimension()

        assert hasattr(parser.grads_ctl, 'xdef')
        xdef = parser.grads_ctl.xdef
        start = 0.0000
        count = 1440
        step = 0.2500
        values = [approx(start+step*n) for n in range(count)]
        assert xdef == {
            'type': 'linear',
            'count': count,
            'start': approx(start),
            'step': approx(step),
            'values': values
        }

    def test_level_dimension_parser(self):
        ctl_content = """zdef   29 levels 
 1000.000000
 962.5000000
 925.0000000
 887.5000000
 850.0000000
 800.0000000
 750.0000000
 700.0000000
 650.0000000
 600.0000000
 550.0000000
 500.0000000
 450.0000000
 400.0000000
 350.0000000
 300.0000000
 275.0000000
 250.0000000
 225.0000000
 200.0000000
 175.0000000
 150.0000000
 125.0000000
 100.0000000
 70.00000000
 50.00000000
 30.00000000
 20.00000000
 10.00000000
 """

        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_dimension()

        assert hasattr(parser.grads_ctl, 'zdef')
        zdef = parser.grads_ctl.zdef
        count = 29
        values = [
            approx(1000.000000),
            approx(962.5000000),
            approx(925.0000000),
            approx(887.5000000),
            approx(850.0000000),
            approx(800.0000000),
            approx(750.0000000),
            approx(700.0000000),
            approx(650.0000000),
            approx(600.0000000),
            approx(550.0000000),
            approx(500.0000000),
            approx(450.0000000),
            approx(400.0000000),
            approx(350.0000000),
            approx(300.0000000),
            approx(275.0000000),
            approx(250.0000000),
            approx(225.0000000),
            approx(200.0000000),
            approx(175.0000000),
            approx(150.0000000),
            approx(125.0000000),
            approx(100.0000000),
            approx(70.00000000),
            approx(50.00000000),
            approx(30.00000000),
            approx(20.00000000),
            approx(10.00000000),
        ]
        assert zdef == {
            'type': 'levels',
            'count': count,
            'values': values
        }

    def test_tdef_parser(self):
        ctl_content = """tdef    1 linear 12z19JAN2018   360mn"""

        parser = GradsCtlParser()
        parser.ctl_file_lines = [l.strip() for l in ctl_content.splitlines()]
        parser.cur_no = 0
        parser.parse_tdef()

        assert hasattr(parser.grads_ctl, 'tdef')
        tdef = parser.grads_ctl.tdef
        start_date = datetime(2018, 1, 19, 12)
        time_step = timedelta(minutes=360)
        count = 1
        values = [start_date + time_step * i for i in range(count)]
        assert tdef == {
            'type': 'linear',
            'count': count,
            'start': start_date,
            'step': time_step,
            'values': values
        }

    def test_vars_parser(self):
        ctl_file = Path(Path(__file__).parent.parent, "data/ctl/grapes_gfs/post.ctl_2018011912_000")

        grads_ctl_parser = GradsCtlParser()
        grads_ctl_parser.parse(str(ctl_file))

        grads_ctl = grads_ctl_parser.grads_ctl

        assert len(grads_ctl.vars) == 55
        assert grads_ctl.vars[0] == {
            'name': 'u',
            'levels': 29,
            'units': '0',
            'description': 'u_wind'
        }

        assert grads_ctl.vars[14] == {
            'name': 'ps',
            'levels': 0,
            'units': '0',
            'description': 'surface pressure'
        }

        record_index = 0
        record = grads_ctl.record[record_index]
        assert record == {
            'name': 'u',
            'level_type': 'multi',
            'level': approx(1000.000000),
            'level_index': 0,
            'units': '0',
            'description': 'u_wind',
            'record_index': record_index
        }

        record_index = 30
        record = grads_ctl.record[record_index]
        assert record == {
            'name': 'v',
            'level_type': 'multi',
            'level': approx(962.5000000),
            'level_index': 1,
            'units': '0',
            'description': 'v_wind',
            'record_index': record_index
        }

        record_index = 356
        record = grads_ctl.record[record_index]
        assert record == {
            'name': 'ps',
            'level_type': 'single',
            'level': 0,
            'level_index': 0,
            'units': '0',
            'description': 'surface pressure',
            'record_index': record_index
        }

    def test_gfs_postvar_ctl(self):
        ctl_file = Path(Path(__file__).parent.parent, "data/ctl/grapes_gfs/post.ctl_2018011912_000")

        grads_ctl_parser = GradsCtlParser()
        grads_ctl_parser.parse(str(ctl_file))

        grads_ctl = grads_ctl_parser.grads_ctl

        assert (grads_ctl.dset ==
                str(Path(Path(__file__).parent.parent, "data/ctl/grapes_gfs/postvar2018011912_000")))
        assert grads_ctl.title == "post output from grapes"
        assert grads_ctl.undef == approx(-9999.0)

