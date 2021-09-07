#!python3
import Adafruit_DHT
import paho.mqtt.client as mqtt  #import the client1
import time

DHT22_PIN = 4

def read_DHT22():
    """
    Reads the DHT22 sensor into a tuple where the first element holds
    the humidity and the second the temperature
    """
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN)
    # Check if ther is a None item in the tuple
    if temp is None or hum is None:
        raise Exception('DHT22 reading exception')
    return (round(hum,1), round(temp,1))

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message =",str(message.payload.decode("utf-8")))

mqtt.Client.connected_flag=False#create flag in class
broker="192.168.11.143"
username="homeassistant"
password="choosoo6Otoh9oe1fiez7Fe0zien1eilai4saiY4ieMiomei3peif2oedeezooSh"
client = mqtt.Client("python1")             #create new instance 
client.on_connect=on_connect  #bind callback function
client.on_message=on_message  #bind callback function
client.loop_start()
client.username_pw_set(username, password=password)
print("Connecting to broker ",broker)
client.connect(broker)      #connect to broker

def validate(val, prev, min, max, diff, desc=""):
    if prev!=None and abs(val-prev)>diff or val<min or val>max:
        logging.debug("{0} value ({1:4.1f}) too extreme. Skipping".format(desc, val))
        return prev
    return round(val, 1)


while not client.connected_flag: #wait in loop
    print("In wait loop")
    time.sleep(1)
print("in Main Loop")
while(True):
    prev_t = None
    prev_h = None
    try:
        hum, temp = read_DHT22()
        hum = validate(hum, prev_h, 1, 100, 10, "Radiator humidity")
        temp = validate(temp, prev_t, 5, 100, 1, "Radiator temp")
        prev_h = hum
        prev_t = temp
        print("Publishing (hum={hum:3.1f},temp={temp:3.1f})".format(hum=hum, temp=temp))
        client.publish("office/radiator/hum", hum)
        client.publish("office/radiator/temp", temp)
    except Exception as e:
        print("Unable to read DHT22")
    time.sleep(10)
client.loop_stop()    #Stop loop 
client.disconnect() # disconnect