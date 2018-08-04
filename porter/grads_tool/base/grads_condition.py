# coding: utf-8


class GradsCondition(object):
    def __init__(self, name, values):
        self.name = name
        self.values = values
        if self.name == 'level':
            self.values = [float(v) for v in self.values]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def is_fit(self, record):
        if self.name == "var":
            if record['name'] in self.values:
                return True
        elif self.name == "level":
            if record['level'] in self.values:
                return True
        else:
            raise Exception("condition not implemented: " + self.name)
        return False
