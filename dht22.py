import os
import logging
try:
    import adafruit_dht
    import board
    _mode = "PI"
except ImportError:
    _mode="DEBUG"
    logging.error("adafruit_dht not imported")

previous_hum = None
previous_temp = None

def init(pin=4):
    global _dhtDevice
    logging.info("Initialyzing DHT22 sensor on pin {}".format(pin))
    _dhtDevice = adafruit_dht.DHT22(pin)
    if _mode=="PI":
        _pin = pin


def read_old():
    """
    Reads the DHT22 sensor into a tuple where the first element holds
    the humidity and the second the temperature
    """
    global previous_hum
    global previous_temp
    logging.debug("Start reading DHT22")
    # Check if ther is a None item in the tuple
    if temp is None or hum is None:
        raise Exception('DHT22 reading exception')
    hum = validate(hum, previous_hum, 0, 100, 1, "Humidity")
    temp = validate(temp, previous_temp, -40, 80, 10, "Temperature")
    return (round(hum,1), round(temp,1))


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


def read():
    global previous_hum
    global previous_temp    
    try:
        logging.debug("Start reading DHT22 sensor")
        # Read the value, or mock
        if _mode=="PI":
            hum = _dhtDevice.humidity
            temp = _dhtDevice.temperature
        else:
            hum = random(0, 100, 10, previous_hum)
            temp = random(5, 50, 5, previous_temp)
        # Check if ther is a None item in the tuple
        if temp is None or hum is None:
            logging.exception('Exception while reading DHT22')
            raise Exception('DHT22 reading exception')
        logging.info("DHT22 hum={hum:3.1f}; temp={temp:3.1f}".format(hum=hum, temp=temp))
        hum = validate(hum, previous_hum, 0, 100, 1, "Humidity")
        temp = validate(temp, previous_temp, 5, 70, 1.5, "Temperature")
        previous_hum = hum
        previous_temp = temp
        return hum, temp
    except Exception as e:
        logging.exception('Exception while reading DHT22')
    return None, None
