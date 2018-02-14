# coding=utf-8
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


from porter.grads_copy import Condition, GradsCopy
from porter.grads_ctl_parser import GradsCtlParser


class TestCondition(object):
    def test_vars_condition(self):
        condition = Condition('var', ['t', 'u', 'v'])

        record = {
            'name': 't',
            'level_type': 'multi',
            'level': 1000.0,
            'level_index': 1,
            'units': 99,
            'description': 'd'
        }

        assert condition.is_fit(record)

        record = {
            'name': 't2m',
            'level_type': 'multi',
            'level': 1000.0,
            'level_index': 1,
            'units': 99,
            'description': 'd'
        }

        assert not condition.is_fit(record)

        condition = Condition('level', [1000, 850, 500])

        record = {
            'name': 't',
            'level_type': 'multi',
            'level': 1000.0,
            'level_index': 1,
            'units': 99,
            'description': 'd'
        }

        assert condition.is_fit(record)

        record = {
            'name': 't2m',
            'level_type': 'multi',
            'level': 900.0,
            'level_index': 1,
            'units': 99,
            'description': 'd'
        }

        assert not condition.is_fit(record)


class TestGradsCopy(object):
    def test_where_parse(self):
        where = "var=t"

        conditions = GradsCopy.parse_where(where)
        assert(len(conditions) == 1)
        assert(conditions[0] == Condition('var', ['t']))

    def test_get_record_list(self):
        grads_ctl_parser = GradsCtlParser()
        ctl_file_path = Path(Path(__file__).parent, "data/ctl/meso/post.ctl_201802120000000")
        grads_ctl = grads_ctl_parser.parse(str(ctl_file_path))

        grads_copy = GradsCopy(where='var=t')
        record_list = grads_copy.get_record_list(grads_ctl)

        assert len(record_list) == 26
        for a_record in record_list:
            assert a_record['name'] == 't'
