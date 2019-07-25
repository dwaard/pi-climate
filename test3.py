import time
import board
import digitalio
import busio
import adafruit_ccs811

i2c_bus = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c_bus)
print("Hello blinka!")
 
# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")
 
# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")
 
# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")
 
print("done!")

# Wait for the sensor to be ready and calibrate the thermistor
while not ccs811.data_ready:
    pass
temp = ccs811.temperature
ccs811.temp_offset = temp - 25.0
 
while True:
    print("CO2: {} PPM, TVOC: {} PPM, Temp: {} C"
          .format(ccs811.eco2, ccs811.tvoc, ccs811.temperature))
    time.sleep(0.5)