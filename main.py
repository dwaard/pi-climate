#!python3
import app
import logging
from time import time, sleep
import board
import busio
import mqtt
import dht22
import bme280
import ccs811

dht22.init(app.env.int("DHT22_PIN", default=17))

logging.debug("Initializing I2C")
i2c_bus = busio.I2C(board.SCL, board.SDA)

bme280.init(i2c_bus, address=int(app.env("BME280_ADDRESS", default=0x76),0))

ccs811.init(i2c_bus)

mqtt.init(app.env("MQTT_BROKER"),
          app.env("MQTT_USER"),
          app.env("MQTT_PWD"))

MEASUREMENT_INTERVAL = app.env.float("MEASUREMENT_INTERVAL", default=10.0)

while(True):
    start_time = time()
    logging.debug("Next iteration")
    try:
        hum, temp = dht22.read()
        mqtt.publish("office/radiator/hum", hum)
        mqtt.publish("office/radiator/temp", temp)
        
        temp, hum, press = bme280.read()
        mqtt.publish("office/temp", temp)
        mqtt.publish("office/hum", hum)
        mqtt.publish("office/press", press)
            
        tvoc, eco2 = ccs811.read()
        mqtt.publish("office/tvoc", tvoc)
        mqtt.publish("office/eco2", eco2)
        
    except Exception as e:
        logging.exception("Unable to perform the iteration")
        
    # Sleep for the rest of the interval_time
    process_time = time() - start_time
    if (process_time < MEASUREMENT_INTERVAL):
        sleep_time = MEASUREMENT_INTERVAL - process_time
        logging.debug("Sleeping for {:f} seconds".format(sleep_time))
        sleep(sleep_time)
    else:
        logging.debug("Skipping sleep")
mqtt.exit()
