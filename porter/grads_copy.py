# coding:utf-8
from porter.grads_ctl_parser import GradsCtlParser


class Condition(object):
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def is_fit(self, record):
        if self.name == "vars":
            if record['name'] in self.values:
                return True
        else:
            raise Exception("condition not implemented: " + self.name)
        return False


class GradsCopy(object):
    def __init__(self, where=None, output=None):
        self.where = where
        self.conditions = self.parse_where(self.where)
        self.output = output

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
            condition = Condition(name, values)
            conditions.append(condition)

        return conditions

    def fit_conditions(self, record):
        for condition in self.conditions:
            if not condition.is_fit(record):
                return False
        return True

    def get_record_list(self, grads_ctl):
        record_list = []
        for a_record in grads_ctl.record:
            if self.fit_conditions(a_record):
                print('Found record:', a_record)
                record_list.append(a_record)
        return record_list

    def process(self, ctl_file):
        grads_ctl_parser = GradsCtlParser()
        grads_ctl = grads_ctl_parser.parse(ctl_file)
        record_list = self.get_record_list(grads_ctl)
