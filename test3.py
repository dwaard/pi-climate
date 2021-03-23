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

DHT22_PIN = 4

# Load the settings from the .env file
load_dotenv()

IN_TEMP = 'field1'
IN_HUM = 'field3'
IN_PRESS = 'field5'
IN_ECO2 = 'field7'
IN_TVOC = 'field8'
OUT_TEMP = 'field2'
OUT_HUM = 'field4'
OUT_PRESS = 'field6'
RAD_TEMP = 'field9'
RAD_HUM = 'field10'
RAD_STATE = 'field11'

LOG_STRING_BME280 = 'Indoor Temp={field1:6.2f}; Hum={field3:5.1f}; Press={field5:6.1f}'
LOG_STRING_DHT22 = 'Radiat Temp={field9:6.2f}; Hum={field10:5.1f}'

LOGGING_FILENAME = "example.log"
LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
LOGGING_LEVEL = 'INFO'
logging.basicConfig(filename=LOGGING_FILENAME, format=LOGGING_FORMAT, level=LOGGING_LEVEL)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def read_DHT22():
    """
    Reads the DHT22 sensor into a tuple where the first element holds
    the humidity and the second the temperature
    """
    logging.debug("Start reading DHT22")
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN)
    # Check if ther is a None item in the tuple
    if temp is None or hum is None:
        logging.exception('Exception while reading DHT22')
        raise Exception('DHT22 reading exception')
    result = {
        RAD_TEMP : round(temp, 2),
        RAD_HUM : round(hum, 2)
    }
    logging.info(LOG_STRING_DHT22.format(**result))
    return result

def switch_fan(state = True):
    key = "cUK5HLYIBik84aaQbZzXh6"
    event = "fan_on"
    if not state:
        event = "fan_off"
    ifttt_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"\
                .format(key=key, event=event)
    logging.info(ifttt_url)
    r = requests.get(url = ifttt_url)

radiator = False
while(True):
    logging.debug('Next iteration')
    dht22_data = read_DHT22()
    rad_temp = dht22_data[RAD_TEMP]
    if not radiator and rad_temp>35:
        switch_fan(True)
        radiator=True
        logging.info("Fan switched ON")
    if radiator and rad_temp<34:
        switch_fan(False)
        radiator=False
        logging.info("Fan switched OFF")
    sleep(10)