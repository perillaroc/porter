# coding: utf-8
from __future__ import print_function, absolute_import
import eccodes
from scipy.interpolate import griddata, interpn, RegularGridInterpolator

from porter.grib_tool.grib_base.grib_condition import GribCondition
from .grib_base.regular_lonlat_grid import RegularLonLatGrid


class GribCopy(object):
    def __init__(self, where, grid_range, output):
        self.where = where
        self.conditions = GribCopy.parse_where(self.where)

        self.grid_range = grid_range
        self.grid = GribCopy.parse_grid_range(grid_range)
        self.output = output

        self.output_file = None

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
        with open(self.output, 'wb') as output_file:
            self.output_file = output_file
            with open(file_path, 'rb') as f:
                while 1:
                    grib_message = eccodes.codes_grib_new_from_file(f)
                    if grib_message is None:
                        break
                    self.process_grib_message(grib_message)

    def process_grib_message(self, grib_message):
        condition_fit = True
        for a_condition in self.conditions:
            if not a_condition.is_fit(grib_message):
                condition_fit = False
                break
        if not condition_fit:
            return
        count = eccodes.codes_get(grib_message, 'count')
        print('processing grib message {count}...'.format(count=count))

        left_lon = eccodes.codes_get(grib_message, 'longitudeOfFirstGridPointInDegrees')
        right_lon = eccodes.codes_get(grib_message, 'longitudeOfLastGridPointInDegrees')
        lon_step = eccodes.codes_get(grib_message, 'iDirectionIncrementInDegrees')
        nx = eccodes.codes_get(grib_message, 'Ni')

        top_lat = eccodes.codes_get(grib_message, 'latitudeOfFirstGridPointInDegrees')
        bottom_lat = eccodes.codes_get(grib_message, 'latitudeOfLastGridPointInDegrees')
        lat_step = eccodes.codes_get(grib_message, 'jDirectionIncrementInDegrees')
        ny = eccodes.codes_get(grib_message, 'Nj')

        orig_values = eccodes.codes_get_values(grib_message)

        orig_grid = RegularLonLatGrid(
            left_lon=left_lon, right_lon=right_lon, lon_step=lon_step,
            top_lat=top_lat, bottom_lat=bottom_lat, lat_step=lat_step
        )
        if self.grid is None:
            self.grid = orig_grid

        self.grid.apply_grid(orig_grid)

        # orig_lons, orig_lats = orig_grid.get_lan_lon_array()
        # target_points = self.grid.get_points()
        # target_lons, target_lats = self.grid.get_lan_lon_array()
        # target_values = griddata((orig_lons, orig_lats), orig_values, target_points, method='linear')

        orig_x_array, orig_y_array = orig_grid.get_xy_array()
        target_xy_points = self.grid.get_xy_points()
        target_function = RegularGridInterpolator((orig_y_array, orig_x_array), orig_values.reshape(ny, nx))
        target_values = target_function(target_xy_points)

        target_x, target_y = self.grid.get_xy_array()

        # target_message = eccodes.codes_new_from_message(grib_message)
        eccodes.codes_set(grib_message, 'longitudeOfFirstGridPointInDegrees', target_x[0])
        eccodes.codes_set(grib_message, 'longitudeOfLastGridPointInDegrees', target_x[-1])
        eccodes.codes_set(grib_message, 'iDirectionIncrementInDegrees', self.grid.lon_step)
        eccodes.codes_set(grib_message, 'Ni', len(target_x))

        eccodes.codes_set(grib_message, 'latitudeOfFirstGridPointInDegrees', target_y[-1])
        eccodes.codes_set(grib_message, 'latitudeOfLastGridPointInDegrees', target_y[0])
        eccodes.codes_set(grib_message, 'jDirectionIncrementInDegrees', self.grid.lat_step)
        eccodes.codes_set(grib_message, 'Nj', len(target_y))
        eccodes.codes_set_values(grib_message, target_values)
        eccodes.codes_write(grib_message, self.output_file)
