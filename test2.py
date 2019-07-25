#this example reads and prints CO2 equiv. measurement, TVOC measurement, and temp every 2 seconds
import sys
from time import sleep
import time
import board
import digitalio
import busio
import adafruit_ccs811
import adafruit_bme280


import Adafruit_DHT

i2c_bus = busio.I2C(board.SCL, board.SDA)

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=0x76)
ccs811 = adafruit_ccs811.CCS811(i2c_bus)


sensor = Adafruit_DHT.DHT22
pin = 22

while(1):
    # Read BMP280 sensor
    t1 = bme280.temperature
    h1 = bme280.humidity
    pressure = bme280.pressure
    
    # Read DHT22 sensor
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    h2, t2 = Adafruit_DHT.read_retry(sensor, pin)
    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    
    if h2 is not None:
        humidity = (h1 + h2) / 2.0        
    else:
        humidity = h1
        
    if t2 is not None:
        temperature = (t1 + t2) / 2.0
    else:
        temperature = t1
        
    # forward humidity and temperature to CCS811 sensor for internal algorithm
    ccs811.set_environmental_data(humidity, temperature)
    # Read CCS811 sensor
    print('Temp={0:4.1f}*C Humidity={1:5.1f}% Pressure={2:6.1f}hpa CO2={3:4d}ppm TVOC={4:3d}ppb'.format(temperature, humidity, pressure, ccs811.eco2, ccs811.tvoc))
    #sys.exit(0)

    sleep(2)
