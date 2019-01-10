# coding:utf-8
from __future__ import print_function, absolute_import

from porter.grads_parser.grads_ctl_parser import GradsCtlParser
from porter.grads_parser.grads_data_handler import GradsDataHandler

from .base.grads_condition import GradsCondition


class GradsCopy(object):
    def __init__(self, where=None, output=None):
        self.where = where
        self.conditions = self.parse_where(self.where)
        if output is None:
            output = 'output.bin'
        self.output = output

    def process(self, ctl_file):
        grads_ctl_parser = GradsCtlParser()
        grads_ctl = grads_ctl_parser.parse(ctl_file)
        filtered_record_list = self.get_filtered_record_list(grads_ctl)
        self.generate_output(grads_ctl, filtered_record_list)

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
            values_string = a_condition_string[index+1:]
            values = values_string.split('|')
            condition = GradsCondition(name, values)
            conditions.append(condition)

        return conditions

    def fit_conditions(self, record):
        for condition in self.conditions:
            if not condition.is_fit(record):
                return False
        return True

    def get_filtered_record_list(self, grads_ctl):
        record_list = []
        for a_record in grads_ctl.record:
            if self.fit_conditions(a_record):
                print('Found record:', a_record)
                record_list.append(a_record)
        return record_list

    def generate_output(self, grads_ctl, record_list):
        data_parser = GradsDataHandler(grads_ctl)
        with open(self.output, 'wb') as output_file:
            with open(grads_ctl.dset, 'rb') as data_file:
                for a_record in record_list:
                    offset = data_parser.get_offset_by_record_index(a_record['record_index'])
                    count = grads_ctl.xdef['count'] * grads_ctl.ydef['count']
                    if 'sequential' in grads_ctl.options:
                        count += 2

                    # load data from file
                    data_file.seek(offset)
                    for _ in range(0, count):
                        output_file.write(data_file.read(4))
