import paho.mqtt.client as mqtt  #import the client1
import logging
import time

data = {}

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logging.info("connected OK")
    else:
        logging.error("Bad connection Returned code=",rc)


def on_message(client, userdata, message):
    time.sleep(1)
    logging.debug("received message =",str(message.payload.decode("utf-8")))


def init(broker, username, password):
    global client
    mqtt.Client.connected_flag=False#create flag in class
    client = mqtt.Client("python1")  #create new instance 
    client.on_connect=on_connect  #bind callback function
    client.on_message=on_message  #bind callback function
    client.username_pw_set(username, password=password)
    client.loop_start()
    logging.info("Connecting to broker {}".format(broker))
    client.connect(broker)      #connect to broker
    while not client.connected_flag: #wait in loop
        logging.debug("Waiting for connection")
        time.sleep(1)
    logging.info("Connected to {}".format(broker))

def exit():
    client.loop_stop()    #Stop loop 
    client.disconnect() # disconnect


def publish(key, value):
    if key not in data:
        data[key] = None
    prev = data[key]
    if value!=prev:
        logging.debug("Publishing {} to {}".format(value, key))
        client.publish(key, value)
        data[key]=prev
