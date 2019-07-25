#this example reads and prints CO2 equiv. measurement, TVOC measurement, and temp every 2 seconds
import sys
from time import sleep
import time
import math
import board
import digitalio
import busio
import adafruit_ccs811
import adafruit_bme280
import urllib.request
import myowm

owm = myowm.OWM(api_key="d6a917a44e771ea2759537287b65472c", q="Middelburg,NL")


def get_dew_point_c(t_air_c, rel_humidity):
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

i2c_bus = busio.I2C(board.SCL, board.SDA)

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=0x76)
ccs811 = adafruit_ccs811.CCS811(i2c_bus)
sleep(1)

# forward humidity and temperature to CCS811 sensor for internal algorithm
temperature = bme280.temperature
humidity = bme280.humidity
ccs811.set_environmental_data(humidity, temperature)

rest_time = 2
sleep_time = 10
request_time = 60 * 5
interval = request_time - 10 * sleep_time

debug_mode = True

while(1):
    try:    
        # Read BME280 sensor
        temperature = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure
        # print(humidity)
        # dewpoint = get_dew_point_c(temperature, humidity)
        
        # forward humidity and temperature to CCS811 sensor for internal algorithm
        ccs811.set_environmental_data(int(humidity), temperature)
        sleep(rest_time) # let the new environmental data settle for a while
        # Read CCS811 sensor
        eco2 = ccs811.eco2
        tvoc = ccs811.tvoc

        if debug_mode:
            print('Temp={0:4.1f}*C  Humidity={1:5.1f}%  Pressure={2:6.1f}hpa  CO2={3:4d}ppm  TVOC={4:3d}ppb'.
                format(temperature, humidity, pressure, eco2, tvoc))
        #sys.exit(0)
        if interval >= request_time:
            owm.fetch()
            
            baseURL = 'https://api.thingspeak.com/update?api_key=DO68GWETIHR6E10S'
            params = '&field1=%s&field2=%s&field3=%s&field4=%s&field5=%s&field6=%s&field7=%s&field8=%s' % (
                temperature, owm.temp, humidity, owm.humidity, pressure, owm.pressure, eco2, tvoc)
            url = baseURL+params
            if debug_mode:
                print (url)
            f = urllib.request.urlopen(baseURL + params)
            f.read()
            f.close()
            interval = 0
    except Exception as e:
        print(e)
        # raise e
        
    sleep(sleep_time - rest_time)
    interval += sleep_time


