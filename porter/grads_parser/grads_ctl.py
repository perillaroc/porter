# coding=utf-8
import sys


class GradsCtl(object):
    __content = dict()

    def __init__(self):
        self.dset = ''
        self.title = ''
        self.options = list()
        self.data_endian = 'little'
        self.local_endian = sys.byteorder
        self.yrev = 0
        self.undef = None

        self.start_time = None
        self.forecast_time = None

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
