# coding: utf-8
from __future__ import print_function, absolute_import
import eccodes
import numpy as np
from scipy.interpolate import griddata

from porter.grib_tool.grib_base.grib_condition import GribCondition


class LonLatGrid(object):
    def __init__(self, left_lon, right_lon, top_lat, bottom_lat, lon_step=None, lat_step=None):
        self.left_lon = LonLatGrid.get_value(left_lon)
        self.right_lon = LonLatGrid.get_value(right_lon)
        self.lon_step = LonLatGrid.get_value(lon_step)
        self.top_lat = LonLatGrid.get_value(top_lat)
        self.bottom_lat = LonLatGrid.get_value(bottom_lat)
        self.lat_step = LonLatGrid.get_value(lat_step)

    @classmethod
    def get_value(cls, value):
        if isinstance(value, float):
            return value
        if value.isdigit():
            return float(value)
        elif value == "-":
            return None
        elif value is None:
            return None
        else:
            raise ValueError("value is error")

    def apply_grid(self, another_grid):
        def apply_attr(name):
            v = getattr(self, name)
            if v is None:
                setattr(self, name, getattr(another_grid, name))
        attr_list = [
            'left_lon',
            'right_lon',
            'lon_step',
            'top_lat',
            'bottom_lat',
            'lat_step',
        ]
        for an_attr_name in attr_list:
            apply_attr(an_attr_name)

    def get_grid_points(self):
        return np.mgrid[self.left_lon:self.right_lon+self.lon_step:self.lon_step,
               self.top_lat:self.bottom_lat-self.lat_step:-1 * self.lat_step]


class GribCopy(object):
    def __init__(self, where, grid_range, output):
        self.where = where
        self.conditions = GribCopy.parse_where(self.where)

        self.grid_range = grid_range
        self.grid = GribCopy.parse_grid_range(grid_range)
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

        grid = LonLatGrid(**params)

        return grid

    def process(self, file_path):
        with open(file_path, 'rb') as f:
            while 1:
                gid = eccodes.codes_grib_new_from_file(f)
                if gid is None:
                    break

                for a_condition in self.conditions:
                    if not a_condition.is_fit(gid):
                        continue

                left_lon = eccodes.codes_get(gid, 'longitudeOfFirstGridPointInDegrees')
                right_lon = eccodes.codes_get(gid, 'longitudeOfLastGridPointInDegrees')
                lon_step = eccodes.codes_get(gid, 'iDirectionIncrementInDegrees')
                nx = eccodes.codes_get(gid, 'Ni')

                top_lat = eccodes.codes_get(gid, 'latitudeOfFirstGridPointInDegrees')
                bottom_lat = eccodes.codes_get(gid, 'latitudeOfLastGridPointInDegrees')
                lat_step = eccodes.codes_get(gid, 'jDirectionIncrementInDegrees')
                ny = eccodes.codes_get(gid, 'Nj')

                orig_values = eccodes.codes_get_values(gid)

                orig_grid = LonLatGrid(
                    left_lon=left_lon, right_lon=right_lon, lon_step=lon_step,
                    top_lat=top_lat, bottom_lat=bottom_lat, lat_step=lat_step
                )
                if self.grid is None:
                    self.grid = orig_grid

                self.grid.apply_grid(orig_grid)

                orig_lons = []
                orig_lats = []
                for y in np.arange(orig_grid.top_lat, orig_grid.bottom_lat - orig_grid.lat_step, -orig_grid.lat_step):
                    for x in np.arange(orig_grid.left_lon, orig_grid.right_lon + orig_grid.lon_step, orig_grid.lon_step):
                        orig_lons.append(x)
                        orig_lats.append(y)

                target_points = []
                for y in np.arange(self.grid.top_lat, self.grid.bottom_lat - self.grid.lat_step, -self.grid.lat_step):
                    for x in np.arange(self.grid.left_lon, self.grid.right_lon + self.grid.lon_step, self.grid.lon_step):
                        target_points.append([x, y])

                orig_grid_x, orig_grid_y = orig_grid.get_grid_points()
                target_grid_x, target_grid_y = self.grid.get_grid_points()

                target_values = griddata((orig_lons, orig_lats), orig_values, target_points, method='linear')
                pass

