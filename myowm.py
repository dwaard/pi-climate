import requests
import json
import math
from datetime import datetime


# Expected response is like:
# {   u'base': u'stations',
#     u'clouds': {   u'all': 64},
#     u'cod': 200,
#     u'coord': {   u'lat': 51.5, u'lon': 3.61},
#     u'dt': 1554562724,
#     u'id': 2750896,
#     u'main': {   u'humidity': 62,
#                  u'pressure': 1004,
#                  u'temp': 13.84,
#                  u'temp_max': 16.67,
#                  u'temp_min': 10.56},
#     u'name': u'Middelburg',
#     u'sys': {   u'country': u'NL',
#                 u'id': 1553,
#                 u'message': 0.0091,
#                 u'sunrise': 1554527419,
#                 u'sunset': 1554575126,
#                 u'type': 1},
#     u'visibility': 9000,
#     u'weather': [   {   u'description': u'haze',
#                         u'icon': u'50d',
#                         u'id': 721,
#                         u'main': u'Haze'}],
#     u'wind': {   u'speed': 1}
# }


class OWM:

    def __init__(self, api_key = '', q='', units='metric'):
        self.api_key = api_key
        self.q = q
        self.units = units

    def fetch(self):
        url = "http://api.openweathermap.org/data/2.5/weather?APPID=%s&q=%s&units=%s" % (
            self.api_key, self.q, self.units
        )
        response = requests.get(url)
        x = response.json()
        if x['cod'] != 200:
            raise ValueError(x['cod'], x['message'])
        self.data = x
        self.timestamp = datetime.fromtimestamp(x['dt'])
        self.temp = x['main']['temp']
        self.humidity = x['main']['humidity']
        self.pressure = x['main']['pressure']
        # self.dewpoint = round(self.compute_dew_point_c(self.temp, self.humidity), 2)

    def compute_dew_point_c(self, t_air_c, rel_humidity):
        """Compute the dew point in degrees Celsius
        :param t_air_c: current ambient temperature in degrees Celsius
        :type t_air_c: float
        :param rel_humidity: relative humidity in %
        :type rel_humidity: float
        :return: the dew point in degrees Celsius
        :rtype: float
        """
        A = 17.27
        B = 237.7
        alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
        return (B * alpha) / (A - alpha)