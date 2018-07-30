# coding: utf-8
import eccodes
from .grib_condition import GribCondition

class GribCopy(object):
    def __init__(self, where, grid_range, output):
        self.where = where
        self.conditions = GribCopy.parse_where(self.where)

        self.grid_range = grid_range
        self.output = output

    def process(self, grib_file):
        pass

    @classmethod
    def parse_where(cls, where):
        """

        :param where:  key[:{s|d|i}]{=|!=}value,key[:{s|d|i}]{=|!=}value,...
        :return:
        """
        conditions = []

        if where is None:
            return conditions

        condition_strings = where.split(',')
        for a_condition_string in condition_strings:
            index = a_condition_string.find('=')
            if index == -1:
                raise Exception("error where cause: " + a_condition_string)

            name = a_condition_string[:index]
            values_string = a_condition_string[index + 1:]
            condition = GribCondition(name, values_string)
            conditions.append(condition)

        return conditions
