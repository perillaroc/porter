# coding: utf-8
import numpy as np


class RegularLonLatGrid(object):
    def __init__(self, left_lon, right_lon, top_lat, bottom_lat, lon_step=None, lat_step=None):
        self.left_lon = RegularLonLatGrid.get_value(left_lon)
        self.right_lon = RegularLonLatGrid.get_value(right_lon)
        self.lon_step = RegularLonLatGrid.get_value(lon_step)
        self.top_lat = RegularLonLatGrid.get_value(top_lat)
        self.bottom_lat = RegularLonLatGrid.get_value(bottom_lat)
        self.lat_step = RegularLonLatGrid.get_value(lat_step)

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
        left_lon = self.left_lon
        right_lon = self.right_lon+self.lon_step
        if right_lon > 360.0:
            right_lon = 360.0
        top_lat = self.top_lat
        bottom_lat = self.bottom_lat - self.lat_step
        if bottom_lat < -90.0:
            bottom_lat = -90.0
        return np.mgrid[left_lon:right_lon:self.lon_step, top_lat:bottom_lat:-self.lat_step]

    def get_points(self):
        lon_step = self.lon_step
        left_lon = self.left_lon
        right_lon = self.right_lon + lon_step
        if right_lon > 360.0:
            right_lon = 360.0
        lat_step = self.lat_step
        top_lat = self.top_lat
        bottom_lat = self.bottom_lat - lat_step
        if bottom_lat < -90.0:
            bottom_lat = -90.0

        points = []
        for y in np.arange(top_lat, bottom_lat, -lat_step):
            for x in np.arange(left_lon, right_lon, lon_step):
                points.append([x, y])
        return points

    def get_lan_lon_array(self):
        lon_step = self.lon_step
        left_lon = self.left_lon
        right_lon = self.right_lon + lon_step
        if right_lon > 360.0:
            right_lon = 360.0
        lat_step = self.lat_step
        top_lat = self.top_lat
        bottom_lat = self.bottom_lat - lat_step
        if bottom_lat < -90.0:
            bottom_lat = -90.0

        lons = []
        lats = []
        for y in np.arange(top_lat, bottom_lat, -lat_step):
            for x in np.arange(left_lon, right_lon, lon_step):
                lons.append(x)
                lats.append(y)
        return lons, lats

    def get_xy_array(self):
        lon_step = self.lon_step
        left_lon = self.left_lon
        right_lon = self.right_lon + lon_step
        if right_lon > 360.0:
            right_lon = 360.0
        lat_step = self.lat_step
        top_lat = self.top_lat
        bottom_lat = self.bottom_lat - lat_step
        if bottom_lat < -90.0:
            bottom_lat = -90.0

        y_array = np.arange(bottom_lat, top_lat, lat_step)
        x_array = np.arange(left_lon, right_lon, lon_step)
        return x_array, y_array

    def get_xy_points(self):
        lon_step = self.lon_step
        left_lon = self.left_lon
        right_lon = self.right_lon + lon_step
        if right_lon > 360.0:
            right_lon = 360.0
        lat_step = self.lat_step
        top_lat = self.top_lat
        bottom_lat = self.bottom_lat - lat_step
        if bottom_lat < -90.0:
            bottom_lat = -90.0

        points = []
        for y in np.arange(bottom_lat, top_lat, lat_step):
            for x in np.arange(left_lon, right_lon, lon_step):
                points.append([y, x])
        return points
