import os
import logging
import signal
import sys
import json
from time import sleep
import os
import subprocess
import time
import paho.mqtt.client as mqtt 
import threading
import hashlib
import database
from config import MQT

# Initialize Logging
logging.basicConfig(level=logging.WARNING)  # Global logging configuration
logger = logging.getLogger("mqtt.MQTT_Server")  # Logger for this module
logger.setLevel(logging.INFO) # Debugging for this file.


    
# Global Variables
BROKER_HOST = MQT.BROKER_HOST
BROKER_PORT = MQT.BROKER_PORT
CLIENT_ID = MQT.CLIENT_ID
TOPIC = MQT.TOPIC

DATA_BLOCK_SIZE = 2000
process = None
client = None  # MQTT client instance. See init_mqtt()
logger = logging.getLogger("mqtt.MQTT_Server")
logger.info("Creating an instance of MQTT_Server")

    
def switch(msg):
    msg_dec = msg.payload.decode("utf-8") # Writes the decoded msg to an object
    msg_top = msg.topic

    if msg_top == 'cycle/init':
        database.addDeviceToDB(msg_dec)

# --- MQTT Related Functions and Callbacks --------------------------------------------------------------

def on_connect( client, user_data, flags, connection_result_code):                              

    if connection_result_code == 0:                                                            
        logger.info("Connected to MQTT Broker")
    else:
        logger.error("Failed to connect to MQTT Broker: " + mqtt.connack_string(connection_result_code))

    client.subscribe(TOPIC)                                                             


def on_disconnect( client, user_data, disconnection_result_code):                               
    logger.error("Disconnected from MQTT Broker")


def on_message( client, user_data, msg): # Callback called when a message is received on a subscribed topic.                                                    
    logger.debug("Received message for topic {}: {}".format( msg.topic, msg.payload))
    switch(msg)


def on_publish(client, user_data, connection_result_code):
    logger.info("Message Published")
    pass


def signal_handler( sig, frame):
    """Capture Control+C and disconnect from Broker."""

    logger.info("You pressed Control + C. Shutting down, please wait...")

    client.disconnect() # Graceful disconnection.
    sys.exit(0)



def init_mqtt():
    global client

    # Our MQTT Client. See PAHO documentation for all configurable options.
    # "clean_session=True" means we don"t want Broker to retain QoS 1 and 2 messages
    # for us when we"re offline. You"ll see the "{"session present": 0}" logged when
    # connected.
    logger.info("Initialising Client")
    client = mqtt.Client(
        client_id=CLIENT_ID,
        clean_session=False)

    # Route Paho logging to Python logging.
    client.enable_logger()

    # Setup callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    
    # Connect to Broker.
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Capture Control + C
    logger.info("Listening for messages on topic '" + str(TOPIC) + "'. Press Control + C to exit.")

    init_mqtt()
    signal.pause()