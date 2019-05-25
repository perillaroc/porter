# coding: utf-8
import nuwe_pyeccodes

from porter.grib_tool.base.grib_condition import GribCondition
from porter.grib_tool.base.regular_lonlat_grid import RegularLonLatGrid


class GribTool(object):
    def __init__(self, where, grid_range):
        self.where = where
        self.conditions = GribTool.parse_where(self.where)

        self.grid_range = grid_range
        self.grid = GribTool.parse_grid_range(grid_range)

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

    @classmethod
    def parse_grid_range(cls, grid_range):
        if grid_range is None:
            return None
        tokens = grid_range.split(',')
        if len(tokens) != 2:
            return None
        params = dict()
        lon_range = tokens[0]
        lon_tokens = lon_range.split('/')
        if len(lon_tokens) == 2:
            params['left_lon'] = lon_tokens[0]
            params['right_lon'] = lon_tokens[1]
        elif len(lon_tokens) == 3:
            params['left_lon'] = lon_tokens[0]
            params['right_lon'] = lon_tokens[1]
            params['lon_step'] = lon_tokens[2]
        else:
            raise Exception("error grid range: " + grid_range)

        lat_range = tokens[1]
        lat_tokens = lat_range.split('/')
        if len(lat_tokens) == 2:
            params['top_lat'] = lat_tokens[0]
            params['bottom_lat'] = lat_tokens[1]
        elif len(lat_tokens) == 3:
            params['top_lat'] = lat_tokens[0]
            params['bottom_lat'] = lat_tokens[1]
            params['lat_step'] = lat_tokens[2]
        else:
            raise Exception("error grid range: " + grid_range)

        grid = RegularLonLatGrid(**params)

        return grid

    def process(self, file_path):
        file_handler = nuwe_pyeccodes.GribFileHandler()
        file_handler.openFile(file_path)
        while 1:
            message_handler = file_handler.next()
            if message_handler is None:
                break
            self.process_grib_message(message_handler)

    def process_grib_message(self, message_handler: nuwe_pyeccodes.GribMessageHandler):
        raise NotImplemented
