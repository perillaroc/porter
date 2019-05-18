# coding: utf-8
from __future__ import print_function, absolute_import

import nuwe_pyeccodes
from scipy.interpolate import griddata, interpn, RegularGridInterpolator

from porter.grib_tool.base.regular_lonlat_grid import RegularLonLatGrid
from porter.grib_tool.grib_tool import GribTool


class GribCopy(GribTool):
    def __init__(self, where, grid_range, output):
        GribTool.__init__(self, where, grid_range)

        self.output = output
        self.output_file = None
        self.message_no = 0

    def process_grib_message(self, message_handler: nuwe_pyeccodes.GribMessageHandler):
        condition_fit = True
        for a_condition in self.conditions:
            if not a_condition.is_fit(message_handler):
                condition_fit = False
                break
        if not condition_fit:
            return
        self.message_no += 1

        count = message_handler.getString('count')
        print('processing grib message {count}...'.format(count=count))

        scanning_mode = message_handler.getLong('scanningMode')

        if scanning_mode != 0:
            raise Exception('scanningMode (value {scanning_mode} not supported. '
                            'Only 0 is supported.')

        left_lon = message_handler.getDouble('longitudeOfFirstGridPointInDegrees')
        right_lon = message_handler.getDouble('longitudeOfLastGridPointInDegrees')
        lon_step = message_handler.getDouble('iDirectionIncrementInDegrees')
        nx = message_handler.getLong('Ni')

        top_lat = message_handler.getDouble('latitudeOfFirstGridPointInDegrees')
        bottom_lat = message_handler.getDouble('latitudeOfLastGridPointInDegrees')
        lat_step = message_handler.getDouble('jDirectionIncrementInDegrees')
        ny = message_handler.getLong('Nj')

        orig_values = message_handler.getDoubleArray(message_handler)

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
        message_handler.setDouble('longitudeOfFirstGridPointInDegrees', target_x[0])
        message_handler.setDouble('longitudeOfLastGridPointInDegrees', target_x[-1])
        message_handler.setDouble('iDirectionIncrementInDegrees', self.grid.lon_step)
        message_handler.setLong('Ni', len(target_x))

        message_handler.setDouble('latitudeOfFirstGridPointInDegrees', target_y[-1])
        message_handler.setDouble('latitudeOfLastGridPointInDegrees', target_y[0])
        message_handler.setDouble('jDirectionIncrementInDegrees', self.grid.lat_step)
        message_handler.setLong('Nj', len(target_y))

        message_handler.setDoubleArray(message_handler, target_values)

        if self.message_no == 1:
            file_mode = "wb"
        else:
            file_mode = "wb+"

        message_handler.save(self.output_file, file_mode)
