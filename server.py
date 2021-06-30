# General Imports
import logging
import os
import database
import time
import threading
import sys
import ssl
from struct import unpack

# Socket Imports
import socket
import tqdm
import pickle
import csv
from config import SOCK

# MQTT Imports
import signal
import json
from time import sleep
import subprocess
import paho.mqtt.client as mqtt 
import threading
from _thread import *
import hashlib
from config import MQT
from database import DATABASE


# Initialize Logging
logging.basicConfig(        filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d, %H:%M:%S',
                            level=logging.INFO)  # Global logging configuration

logger = logging.getLogger("SERVER")  # Logger for this module
'''
output_file_handler = logging.FileHandler("server.log")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
'''

# --- AWS Logging
logging.basicConfig(        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d, %H:%M:%S',
                            level=logging.INFO)
logger = logging.getLogger()


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)


def launch_socket():

    # device's IP address
    SERVER_HOST = SOCK.SERVER_HOST
    SERVER_PORT = SOCK.SERVER_PORT
    SERVER_CERT = SOCK.SERVER_CERT
    SERVER_KEY = SOCK.SERVER_KEY
    CA_CERT = SOCK.CA_CERT

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    context.load_verify_locations(cafile=CA_CERT)


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket Object
    s.bind((SERVER_HOST, SERVER_PORT)) # Bind The Socket To Our Server Port
    s.listen(5) # Listen, allow 5 pending requests
    logger.info('SOCKET - '+ f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    BUFFER_SIZE = 4096  # Receive 4096 Bytes In Each Transmission
    SEPARATOR = "<SEPARATOR>"
            
    def handle_message(msg):
        try:
            DB = DATABASE(msg)
            DB.write_to_db()
        except Exception as e:
            print(e)

    def multi_threaded_client(conn):
        
        while True:
            received = conn.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)
            filename = os.path.basename(filename)
            filesize = int(filesize)
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=BUFFER_SIZE)

            try:
                bs = conn.recv(4096)
                (length,) = unpack('>Q', bs)
                buffer = b""
                while len(buffer) < length:
                    to_read = length - len(buffer)
                    buffer += conn.recv(
                        4096 if to_read > 4096 else to_read)
                    progress.update(len(buffer))
                progress.close()
                
                assert len(b'\00') == 1
                conn.sendall(b'\00')
            finally:
                conn.shutdown(socket.SHUT_WR)
                logger.info("SOCKET - Client Socket Shutdown")
                conn.close()
            
            try:
                buffer = buffer.decode("utf-8")
            except:
                buffer = pickle.loads(buffer)

            print(buffer)
            handle_message(buffer)
            logger.info("SOCKET - Submitted To Database")

            sys.exit()


    def wrappedSocket():
        while True:
            client_socket, address = s.accept()
            logger.info('SOCKET - ' + f"[+] {address} is connected.")
            try:
                #conn = context.wrap_socket(client_socket, server_side=True) 
                #logger.info("SSL established. Peer: {}".format(conn.getpeercert())) 
                start_new_thread(multi_threaded_client, (client_socket,))
            except Exception as e:
                print(e)
                logger.error('Unauthorised Access Attempt')
                
   
    if __name__ == "__main__":
       wrappedSocket()


def launch_mqtt():

    # Global Variables
    BROKER_HOST = MQT.BROKER_HOST
    BROKER_PORT = MQT.BROKER_PORT
    CLIENT_ID = MQT.CLIENT_ID
    TOPIC = MQT.TOPIC

    DATA_BLOCK_SIZE = 2000
    process = None
    client = None  # MQTT client instance. See init_mqtt()
    logger.info("MQTT - Creating MQTT Instance")

    # --- MQTT Related Functions and Callbacks --------------------------------------------------------------

    def on_connect( client, user_data, flags, connection_result_code):                              

        if connection_result_code == 0:                                                            
            logger.info("MQTT - Connected to Broker")
        else:
            logger.error("MQTT - Failed to connect to Broker: " + mqtt.connack_string(connection_result_code))

        client.subscribe(TOPIC)                                                             


    def on_disconnect( client, user_data, disconnection_result_code):                               
        logger.error("MQTT - Disconnected from Broker")


    def handle_message(msg):
        print(msg)
        try:
            DB = DATABASE(msg)
            DB.write_to_db()
        except Exception as e:
            print(e)


    def on_message( client, user_data, msg): # Callback called when a message is received on a subscribed topic.                                                    
        logger.info("MQTT - Received message for topic {}: {}".format( msg.topic, pickle.loads(msg.payload)))
        handle_message(pickle.loads(msg.payload))


    def on_publish(client, user_data, connection_result_code):
        logger.info("MQTT - Message Published")
        pass


    def main():
        global client

        # Our MQTT Client. See PAHO documentation for all configurable options.
        # "clean_session=True" means we don"t want Broker to retain QoS 1 and 2 messages
        # for us when we"re offline. You"ll see the "{"session present": 0}" logged when
        # connected.
        logger.info("MQTT - Initialising Client")
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
        while True:
            try:
                client.connect(BROKER_HOST, BROKER_PORT)
                break
            except:
                logger.error("MQTT - Failed to connect to broker. Retrying...")
            finally:
                time.sleep(5)

        client.loop_forever()


    if __name__ == "__main__":
        main()
        logger.info("MQTT - Listening for messages on topic '" + str(TOPIC))


if __name__ == "__main__":
    t1 = threading.Thread(target=launch_socket)
    t2 = threading.Thread(target=launch_mqtt)
    t1.start()
    t2.start()
   #launch_mqtt()