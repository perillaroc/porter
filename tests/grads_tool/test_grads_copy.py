# coding=utf-8
from pathlib import Path

import pytest

from porter.grads_tool.grads_copy import GradsCopy
from porter.grads_tool.base.grads_condition import GradsCondition
from porter.grads_parser.grads_ctl_parser import GradsCtlParser


class TestCondition(object):
    def test_constructor(self):
        condition = GradsCondition('var', ['t', 'u', 'v'])

        condition = GradsCondition('level', [1000, 850, 500])
        condition = GradsCondition('level', ['1000', '850', '500'])
        with pytest.raises(ValueError):
            condition = GradsCondition('level', ['t', 'u', 'v'])

    def test_vars_condition(self):
        condition = GradsCondition('var', ['t', 'u', 'v'])

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

        condition = GradsCondition('level', [1000, 850, 500])

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

        condition = GradsCondition('UNKNOWN', [1000, 850, 500])

        record = {
            'name': 't2m',
            'level_type': 'multi',
            'level': 900.0,
            'level_index': 1,
            'units': 99,
            'description': 'd'
        }

        with pytest.raises(Exception):
            condition.is_fit(record)

    def test_condition_equal(self):
        condition_a = GradsCondition('var', ['t', 'u', 'v'])
        condition_b = GradsCondition('var', ['t', 'u', 'v'])
        assert condition_a == condition_b

        condition_a = GradsCondition('var', ['t', 'u', 'v'])
        condition_b = GradsCondition('var', ['t', 'u'])
        assert not condition_a == condition_b

        condition_a = GradsCondition('var', ['t', 'u', 'v'])
        condition_b = GradsCondition('level', [1000, 875])
        assert not condition_a == condition_b


class TestGradsCopy(object):
    def test_single_where_single_value(self):
        where = "var=t"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 1
        assert conditions[0] == GradsCondition('var', ['t'])

        where = "level=1000"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 1
        assert conditions[0] == GradsCondition('level', ['1000'])

    def test_single_where_multi_value(self):
        where = "var=t|u"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 1
        assert conditions[0] == GradsCondition('var', ['t', 'u'])

        where = "level=1000|875"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 1
        assert (conditions[0] == GradsCondition('level', ['1000', '875']))

    def test_multi_where_single_value(self):
        where = "var=t,level=1000"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 2
        assert conditions[0] == GradsCondition('var', ['t'])
        assert conditions[1] == GradsCondition('level', ['1000'])

    def test_multi_where_multi_value(self):
        where = "var=t|u,level=1000|875"
        conditions = GradsCopy.parse_where(where)
        assert len(conditions) == 2
        assert conditions[0] == GradsCondition('var', ['t', 'u'])
        assert conditions[1] == GradsCondition('level', ['1000', '875'])

    def test_get_record_list(self):
        grads_ctl_parser = GradsCtlParser()
        ctl_file_path = Path(Path(__file__).parent.parent, "data/ctl/meso/post.ctl_201802120000000")
        grads_ctl = grads_ctl_parser.parse(str(ctl_file_path))

        grads_copy = GradsCopy(where='var=t')
        record_list = grads_copy.get_filtered_record_list(grads_ctl)

        assert len(record_list) == 26
        for a_record in record_list:
            assert a_record['name'] == 't'
