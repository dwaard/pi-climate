import os
import logging
import random
from time import sleep
try:
    import adafruit_ccs811
    _mode = "PI"
except ImportError:
    _mode="DEBUG"


_ccs811 = None

_previous_tvoc = None
_previous_eco2 = None

def init(i2c_bus, set_env_data=0, settle_time=1.0):
    global CCS811_SET_ENV_DATA
    global CCS811_SETTLE_TIME
    CCS811_SET_ENV_DATA = set_env_data
    CCS811_SETTLE_TIME = settle_time
    if _mode=="PI":
        global _ccs811
        logging.info("Initialyzing CCS811 sensor with no address specified")
        _ccs811 = adafruit_ccs811.CCS811(i2c_bus)
        sleep(settle_time)


def set_env_data():
    # forward humidity and temperature to CCS811 sensor for internal algorithm
    if(CCS811_SET_ENV_DATA>0) and _mode=="PI":
        #TODO implement the bme280 data here
        _ccs811.set_environmental_data(int(bme280[IN_HUM]), bme280[IN_TEMP])
        sleep(CCS811_SETTLE_TIME) # let the new environmental data settle for a while


def validate(val, prev, minv, maxv, diff, desc=""):
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


def read_eco2():
    global _previous_eco2
    # Read the value, or mock
    if _mode=="PI":
        value = _ccs811.eco2
    else:
        value = random(400, 8192, 50, _previous_eco2)
    # validate new value. Use previous when value is too extreme
    value = validate(value, _previous_eco2, 400, 8192, 50, "ECo2")
    _previous_eco2 = value
    return value


def read_tvoc():
    global _previous_tvoc
    # Read the value, or mock
    if _mode=="PI":
        global _ccs811
        value = _ccs811.tvoc
    else:
        value = random(0, 1187, 10, _previous_tvoc)
    # validate new value. Use previous when value is too extreme
    value = validate(value, _previous_tvoc, 0, 1187, 10, "TVOC")
    _previous_tvoc = value
    return value


def read():
    global _prev
    logging.debug("Start reading CCS811 sensor")
    try:
        set_env_data()
        tvoc = read_tvoc()
        eco2 = read_eco2()
        logging.info("CCS811 tvoc={tvoc:4.1f}; eco2={eco2:5.1f}".\
            format(tvoc=tvoc, eco2=eco2))
        return tvoc, eco2
    except Exception as e:
        logging.exception('Exception while reading CCS811')
    return None, None
