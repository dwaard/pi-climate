#!python3
import app
from envparse import env
import dht22
import bme280
import ccs811
import mqtt
import time
try:
    import board
    import busio
    _mode = "PI"
except Exception:
    _mode="DEBUG"


if __name__ == '__main__':
    # Initialize I2C components
    i2c_bus = None
    if _mode=="PI":
        i2c_bus = busio.I2C(board.SCL, board.SDA)
    ccs811.init(i2c_bus, \
        set_env_data=env.int("CCS811_SET_ENV_DATA", default=0), \
            settle_time=env.float("CCS811_SETTLE_TIME", default=1.0))
    bme280.init(i2c_bus, \
        address=app.parseIntThatMightBeHex(env("BME280_ADDRESS", default=0x76)))
    dht22.init(pin=env.int("DHT22_PIN", default=4))
    mqtt.init(broker=env("MQTT_BROKER"), username=env("MQTT_USER"), \
        password=env("MQTT_PWD"))
    hum, temp = dht22.read()
    mqtt.publish("test/dht22/humidity", hum)
    mqtt.publish("test/dht22/temperature", temp)
    temp, hum, press = bme280.read()
    mqtt.publish('test/bme280/tempreature', temp)
    mqtt.publish('test/bme280/humidity', hum)
    mqtt.publish('test/bme280/pressure', press)
    tvoc, eco2 = ccs811.read()
    mqtt.publish('test/ccs811/tvoc', tvoc)
    mqtt.publish('test/ccs811/eco2', eco2)
    time.sleep(1)
    hum, temp = dht22.read()
    mqtt.publish("test/dht22/humidity", hum)
    mqtt.publish("test/dht22/temperature", temp)
