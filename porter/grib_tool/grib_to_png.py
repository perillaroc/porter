# coding: utf-8
import nuwe_pyeccodes
import numpy as np
from PIL import Image
import json


from porter.grib_tool.grib_tool import GribTool


class GribConverter(object):
    def __init__(self, where, output):
        self.where = where
        self.conditions = GribTool.parse_where(self.where)
        self.output = output
        self.output_file = None

    def process(self, file_path):
        file_handler = nuwe_pyeccodes.GribFileHandler()
        file_handler.openFile(file_path)
        while 1:
            message_handler = file_handler.next()
            if message_handler is None:
                break
            self.process_grib_message(message_handler)

    def process_grib_message(self, message_handler):
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

        values = message_handler.getDoubleArray('values')
        values = values.reshape(ny, nx)

        min_value = np.max(values)
        max_value = np.min(values)

        values = (values - min_value) / (max_value-min_value) * 255

        im = Image.fromarray(values)
        im = im.convert("L")
        im.save("{output_file}.{count}.png".format(output_file=self.output, count=count))

        image_info = {
            'min_value': min_value,
            'max_value': max_value,
            'left_lon': left_lon,
            'right_lon': right_lon,
            'lon_step': lon_step,
            'nx': nx,
            'top_lat': top_lat,
            'bottom_lat': bottom_lat,
            'lat_step': lat_step,
            'ny': ny
        }
        with open("{output_file}.{count}.json".format(output_file=self.output, count=count), "w") as f:
            json.dump(image_info, f, indent=2)
