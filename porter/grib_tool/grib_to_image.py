# coding: utf-8
import json

import nuwe_pyeccodes
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from PIL import Image


from porter.grib_tool.base.grib_tool import GribTool
from porter.grib_tool.base.regular_lonlat_grid import RegularLonLatGrid


class GribToImageConverter(GribTool):
    def __init__(self, where, grid_range, output, image_type):
        GribTool.__init__(self, where, grid_range)
        self.output = output
        self.output_file = None
        self.image_type = image_type

    def process_grib_message(self, message_handler: nuwe_pyeccodes.GribMessageHandler):
        condition_fit = True
        for a_condition in self.conditions:
            if not a_condition.is_fit(message_handler):
                condition_fit = False
                break
        if not condition_fit:
            return

        count = message_handler.getLong('count')

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

        orig_grid = RegularLonLatGrid(
            left_lon=left_lon, right_lon=right_lon, lon_step=lon_step,
            top_lat=top_lat, bottom_lat=bottom_lat, lat_step=lat_step
        )
        if self.grid is None:
            self.grid = orig_grid

        self.grid.apply_grid(orig_grid)

        values = message_handler.getDoubleArray('values')
        values = values.reshape(ny, nx)

        min_value = np.max(values)
        max_value = np.min(values)

        values = (values - min_value) / (max_value-min_value) * 255

        orig_x_array, orig_y_array = orig_grid.get_xy_array()
        target_xy_points = self.grid.get_xy_points()
        target_x, target_y = self.grid.get_xy_array()

        target_function = RegularGridInterpolator((orig_y_array, orig_x_array), values)
        target_values = target_function(target_xy_points).reshape(len(target_y), len(target_x))

        im = Image.fromarray(target_values)
        im = im.convert("L")
        image_extension = 'png'
        image_extension_mapper = {
            'png': 'png',
            'jpeg': 'jpg',
            'jpg': 'jpg',
        }
        if self.image_type in image_extension_mapper:
            image_extension = image_extension_mapper[self.image_type]
        else:
            print("using default image file type: png")
        im.save("{output_file}.{count}.{image_extension}".format(
            output_file=self.output,
            count=count,
            image_extension=image_extension
        ))

        image_info = {
            'min_value': min_value,
            'max_value': max_value,
            'left_lon': self.grid.left_lon,
            'right_lon': self.grid.right_lon,
            'lon_step': self.grid.lon_step,
            'nx': len(target_x),
            'top_lat': self.grid.top_lat,
            'bottom_lat': self.grid.bottom_lat,
            'lat_step': self.grid.lat_step,
            'ny': len(target_y)
        }
        with open("{output_file}.{count}.json".format(output_file=self.output, count=count), "w") as f:
            json.dump(image_info, f, indent=2)
