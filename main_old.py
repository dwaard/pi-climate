import sys
import os
import logging
import requests
import json
from dotenv import load_dotenv
from time import sleep
from time import time
import board
import busio
import adafruit_ccs811
import adafruit_bme280
import urllib.request

# Load the settings from the .env file
load_dotenv()

# global constants and configuration
LOGGING_FILENAME = os.getenv('LOGGING_FILENAME')
LOGGING_FORMAT = os.getenv('LOGGING_FORMAT')
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL')
# Initialize logging
logging.basicConfig(
    filename=LOGGING_FILENAME,
    format=LOGGING_FORMAT, 
    level=LOGGING_LEVEL
    )

MEASUREMENT_INTERVAL = float(os.getenv("MEASUREMENT_INTERVAL"))
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL"))
last_request_time = 0

BME280_ADDRESS = int(os.getenv("BME280_ADDRESS"), 0)
CCS811_SETTLE_TIME = float(os.getenv("CCS811_SETTLE_TIME"))
# Initialize the I2C bus and components
i2c_bus = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=BME280_ADDRESS)
ccs811 = adafruit_ccs811.CCS811(i2c_bus)
# Make sure all is well on the I2C side
sleep(CCS811_SETTLE_TIME)

OWM_API_KEY = os.getenv("OWM_API_KEY")
OWM_QUERY = os.getenv("OWM_QUERY")

THINGSPEAK_API_KEY=os.getenv('THINGSPEAK_API_KEY')


def fetch_owm_data(api_key='', query='', units='metric'):
    url = "http://api.openweathermap.org/data/2.5/weather?appid={}&{}&units={}".format(api_key, query, units) 
    response = requests.get(url)
    x = response.json()
    if x['cod'] != 200:
        raise ValueError(x['cod'], x['message'])
    temp = x['main']['temp']
    humidity = x['main']['humidity']
    pressure = x['main']['pressure']
    return (temp, humidity, pressure)


def init():
    global last_request_time
    last_request_time = time()



def loop():
    start_time = time()
    logging.debug("start loop at {}".format(start_time))

    # Read BME280 sensor
    part1 = ''    
    try:
        temperature = bme280.temperature
        humidity = bme280.humidity
        pressure = bme280.pressure
        part1 = '&field1={field1:.2f}&field3={field3:.1f}&field5={field5:.1f}'.format(field1=temperature, field3=humidity, field5=pressure)
        logging.info('Temperature={:6.2f}; Humidity={:5.1f}; Pressure={:6.1f}'.format(temperature, humidity, pressure))
    except Exception as e:
        logging.exception('Exception while reading BME280')
    # Read CCS811(co2,tvoc) sensor
    part2 = ''
    try:
        # forward humidity and temperature to CCS811 sensor for internal algorithm
        ccs811.set_environmental_data(int(humidity), temperature)
        sleep(CCS811_SETTLE_TIME) # let the new environmental data settle for a while
        eco2 = ccs811.eco2
        tvoc = ccs811.tvoc
        part2 = '&field7={field7:d}&field8={field8:d}'.format(field7=eco2, field8=tvoc)
        logging.info('ECO2={:4d}; TVOC={:4d}'.format(eco2, tvoc))
    except Exception as e:
        logging.exception('Exception while reading CCS811')

    # Check and handle Request interval
    global last_request_time    
    if (start_time - last_request_time) >= REQUEST_INTERVAL:
        logging.info("Request interval started")
        last_request_time = start_time
        # Fetch data from Open Wheather Map service
        part3=''
        try:
            owm_temp, owm_hum, owm_press = fetch_owm_data(api_key=OWM_API_KEY, query=OWM_QUERY)
            part3 = '&field2={field2:.2f}&field4={field4:d}&field6={field6:d}'.format(field2=owm_temp, field4=owm_hum, field6=owm_press)
            logging.info('Outdoor Temperature={:6.2f}; Humidity={:5.1f}; Pressure={:6.1f}'.format(owm_temp, owm_hum, owm_press))
        except Exception as e:
            logging.exception('Exception while reading Wheather service')
        # Send data to Thingspeak
        try:    
            baseURL = 'https://api.thingspeak.com/update?api_key={}'.format(THINGSPEAK_API_KEY)
            url = baseURL+part1+part2+part3
            logging.debug(url)
            f = urllib.request.urlopen(url)
            f.read()
            f.close()
        except Exception as e:
            logging.exception('Exception while sending to Thingspeak')

    # Sleep for the rest of the interval_time    
    process_time = time() - start_time
    sleep_time = MEASUREMENT_INTERVAL - process_time
    if (sleep_time > 0):
        logging.debug("Sleeping for {:f} seconds".format(sleep_time))
        sleep(sleep_time)
    else:
        logging.debug("Skipping sleep")

def main():
    try:
        init()
    except Exception:
        logging.exception("Fatal error in main init. Program will terminate")
        sys.exit(1)

    while(1):
        try:
            loop()
        except Exception:
            logging.exception("Fatal error in main loop")
            sleep(MEASUREMENT_INTERVAL)

if __name__ == '__main__':
    main()
