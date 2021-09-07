import os
import logging
import random
try:
    import adafruit_bme280
    _mode = "PI"
except ImportError:
    _mode="DEBUG"

_bme280 = None

previous_temp = None
previous_hum = None
previous_press = None

def init(i2c_bus, address=0):
    global _heat_up
    _heat_up = 3 * 20
    if _mode=="PI":
        global _bme280
        logging.info("Initialyzing BME280 sensor on address {}".format(address))
        _bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=address)

def validate(val, prev, minv, maxv, diff, desc=""):
    global _heat_up
    if _heat_up > 0:
        _heat_up -= 1
        return round(val,1)
    if prev!=None and abs(val-prev)>diff or val<minv or val>maxv:
        logging.warning("{0} value ({1:4.1f}) too extreme. Skipping".format(desc, val))
        return prev
    return round(val, 1)


def random(vmin, vmax, vdiff, vprev):
    if not vprev:
        return random.uniform(vmin, vmax)
    return random.uniform(
        max(vmin, vprev-vdiff),
        min(vmax, vprev_vdiff)
    )


def read_temperature():
    global previous_temp
    # Read the value, or mock
    if _mode=="PI":
        value = _bme280.temperature
    else:
        value = random(5, 50, 0.5, previous_temp)
    value = round(value, 2)
    value = validate(value, previous_temp, 5, 50, 0.5, "Temperature")
    previous_temp = value
    return value

def read_humidity():
    global previous_hum
    # Read the value, or mock
    if _mode=="PI":
        value = _bme280.humidity
    else:
        value = random(0, 100, 1, previous_hum)
    value = round(value, 2)
    value = validate(value, previous_hum, 0, 100, 1, "Humidity")
    previous_hum = value
    return value


def read_pressure():
    global previous_press
    # Read the value, or mock
    if _mode=="PI":
        value = _bme280.pressure
    else:
        value = random(475, 1100, 10, previous_pres)
    value = round(value, 1)
    # validate new value. Use previous when value is too extreme 
    value = validate(value, previous_press, 475, 1100, 10, "Pressure")
    previous_press = value
    return value


def read():
    logging.debug("Start reading BME280 sensor")
    try:
        temp = read_temperature()
        hum = read_humidity()
        press = read_pressure()
        logging.info("BME280 temp={temp:4.1f}; hum={hum:5.1f}; press={press:6.1f}".\
            format(temp=temp, hum=hum, press=press))
        return temp, hum, press
    except Exception as e:
        logging.exception('Exception while reading BME280')
        return None, None, None
