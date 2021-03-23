import sys
import os
import logging
import requests
import json
from dotenv import load_dotenv
from time import time, sleep
import board
import busio
import adafruit_ccs811
import adafruit_bme280
import Adafruit_DHT

IN_TEMP = 'field1'
IN_HUM = 'field3'
IN_PRESS = 'field5'
IN_ECO2 = 'field7'
IN_TVOC = 'field8'
OUT_TEMP = 'field2'
OUT_HUM = 'field4'
OUT_PRESS = 'field6'

DHT22_PIN = 4

LOG_STRING_BME280 = 'Indoor Temp={field1:6.2f}; Hum={field3:5.1f}; Press={field5:6.1f}'
LOG_STRING_CCS811 = 'ECO2={field7:4d}; TVOC={field8:4d}'
LOG_STRING_OWM = 'Outdoor Temp={field2:6.2f}; Hum={field4:5.1f}; Press={field6:6.1f}'

# Load the settings from the .env file
load_dotenv()

# global constants and configuration
LOGGING_FILENAME = os.getenv('LOGGING_FILENAME')
LOGGING_FORMAT = os.getenv('LOGGING_FORMAT')
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL')
# Initialize logging
logging.basicConfig(filename=LOGGING_FILENAME, format=LOGGING_FORMAT, level=LOGGING_LEVEL)

MEASUREMENT_INTERVAL = float(os.getenv("MEASUREMENT_INTERVAL"))
REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL"))
last_request_time = 0

BME280_ADDRESS = int(os.getenv("BME280_ADDRESS"), 0)
CCS811_SET_ENV_DATA = int(os.getenv("CCS811_SET_ENV_DATA"), 0)
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


def init():
    global last_request_time
    last_request_time = 0


def read_bme280():
    logging.debug("Start reading BME280 sensor")
    result = {}
    try:
        result[IN_TEMP] = round(bme280.temperature,2)
        result[IN_HUM] = round(bme280.humidity,2)
        result[IN_PRESS] = round(bme280.pressure,1)
        logging.info(LOG_STRING_BME280.format(**result))
    except Exception as e:
        logging.exception('Exception while reading BME280')
    return result


def read_ccs811(bme280):
    logging.debug("Start reading CCS811 sensor")
    result = {}
    try:
        # forward humidity and temperature to CCS811 sensor for internal algorithm
        if(CCS811_SET_ENV_DATA>0):
            ccs811.set_environmental_data(int(bme280[IN_HUM]), bme280[IN_TEMP])
            sleep(CCS811_SETTLE_TIME) # let the new environmental data settle for a while
        result[IN_ECO2] = ccs811.eco2
        result[IN_TVOC] = ccs811.tvoc
        logging.info(LOG_STRING_CCS811.format(**result))
    except Exception as e:
        logging.exception('Exception while reading CCS811')
    return result


def read_owm():
    logging.debug("Start reading OWM service")
    result = {}
    try:
        # Transform OWM_QUERY to a dict so it can be passed to the wom service in the url
        params = {x[0] : x[1] for x in [y.split("=") for y in OWM_QUERY.split("&") ]}
        params['appid'] = OWM_API_KEY
        params['units'] = 'metric'
        response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)
        logging.debug("Received: {}".format(response.text))
        response_json = response.json()
        if response_json['cod'] != 200:
            logging.error(response_json['message'])
            response.raise_for_status()
        result[OUT_TEMP] = response_json['main']['temp']
        result[OUT_HUM] = response_json['main']['humidity']
        result[OUT_PRESS] = response_json['main']['pressure']
        logging.info(LOG_STRING_OWM.format(**result))
    except Exception as e:
        logging.exception('Exception while reading Wheather service')
        raise e
    return result

def read_DHT22():
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    hum = round(hum, 2)
    temp= round(temp, 2)
    # Check if data is valid
    if hum is None or temp is None:
        logging.exception('Exception while reading DHT22')
    return (hum, temp)


def send_to_thingspeak(data):
    logging.debug("Start sending data to Thingspeak channel")
    if len(data)==0:
        logging.warning("Try to send empty data array to Thingspeak. Skipping this.")
    else:
        try:
            # Add api_key to data, so the data dict can be processed with the other params 
            # in the request.
            data['api_key'] = THINGSPEAK_API_KEY
            response = requests.get('https://api.thingspeak.com/update', params=data)
            if response.status_code != 200:
                response.raise_for_status()
            logging.debug("Received: {}".format(response.text))
        except Exception as e:
            logging.exception('Exception while sending to Thingspeak')


def loop():
    start_time = time()
    logging.debug("Starting another loop")
    # Read BME280 and CCS811 sensors
    bme280_data = read_bme280()
    ccs811_data = read_ccs811(bme280_data)
    # Check and handle Request interval
    global last_request_time    
    if (start_time - last_request_time) >= REQUEST_INTERVAL:
        logging.info("Request interval started")
        last_request_time = start_time
        # Fetch data from Open Wheather Map service
        owm_data = read_owm()
        # Send data to Thingspeak
        send_to_thingspeak({**bme280_data, **ccs811_data, **owm_data})
    # Sleep for the rest of the interval_time    
    process_time = time() - start_time
    if (process_time < MEASUREMENT_INTERVAL):
        sleep_time = MEASUREMENT_INTERVAL - process_time
        logging.debug("Sleeping for {:f} seconds".format(sleep_time))
        sleep(sleep_time)
    else:
        logging.debug("Skipping sleep")


if __name__ == '__main__':
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
