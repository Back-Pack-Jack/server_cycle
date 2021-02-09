# General Imports
import logging
import os
import database
import time
import threading

# Socket Imports
import socket
import tqdm
import pickle
import csv
from config import SOCK

# MQTT Imports
import signal
import sys
import json
from time import sleep
import subprocess
import paho.mqtt.client as mqtt 
import threading
import hashlib
from config import MQT


# Initialize Logging
logging.basicConfig(level=logging.WARNING)  # Global logging configuration
logger = logging.getLogger("SERVER")  # Logger for this module
logger.setLevel(logging.INFO) # Debugging for this file.


def launch_socket():

    # device's IP address
    SERVER_HOST = SOCK.SERVER_HOST
    SERVER_PORT = SOCK.SERVER_PORT

    BUFFER_SIZE = 4096  # Receive 4096 Bytes In Each Transmission
    SEPARATOR = "<SEPARATOR>"

    s = socket.socket() # Create The Server Socket
    s.bind((SERVER_HOST, SERVER_PORT)) # Bind The Socket To Our Local Address

    # --- Enabling our server to accept connections
    # --- 5 here is the number of accepted connections that
    # --- the system will allow before refusing new connections
    s.listen(5)
    logger.info('SOCKET - '+ f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    def main():
        # accept connection if there is any
        while True:
            client_socket, address = s.accept() 
            # if below code is executed, that means the sender is connected
            logger.info('SOCKET - ' + f"[+] {address} is connected.")

            # receive the file infos
            # receive using client socket, not server socket
            received = client_socket.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            # convert to integer
            filesize = int(filesize)


            # start receiving the file from the socket
            # and writing to the file stream
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

            buffer = b''
            while True:
                try:
                    for _ in progress:
                        # read 1024 bytes from the socket (receive)
                        bytes_read = client_socket.recv(BUFFER_SIZE)
                        logger.info(bytes_read)
                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done
                            break
                        # write to the file the bytes we just received
                        #f.write(bytes_read)
                        buffer += bytes_read
                        # update the progress bar
                        progress.update(len(bytes_read))
                finally:
                    output = pickle.loads(buffer)
                    logger.info('SOCKET - output: {}'.format(output))
                    database.writeToDatabase(output)
                    break

                # close the client socket
                client_socket.close()
                # close the server socket
                s.close()
   
    if __name__ == "__main__":
       main()

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

        
    def switch(msg):
        msg_dec = msg.payload.decode("utf-8") # Writes the decoded msg to an object
        msg_top = msg.topic

        if msg_top == 'cycle/init':
            database.addDeviceToDB(msg_dec)

    # --- MQTT Related Functions and Callbacks --------------------------------------------------------------

    def on_connect( client, user_data, flags, connection_result_code):                              

        if connection_result_code == 0:                                                            
            logger.info("MQTT - Connected to Broker")
        else:
            logger.error("MQTT - Failed to connect to Broker: " + mqtt.connack_string(connection_result_code))

        client.subscribe(TOPIC)                                                             


    def on_disconnect( client, user_data, disconnection_result_code):                               
        logger.error("MQTT - Disconnected from Broker")


    def on_message( client, user_data, msg): # Callback called when a message is received on a subscribed topic.                                                    
        logger.debug("MQTT - Received message for topic {}: {}".format( msg.topic, msg.payload))
        switch(msg)


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

        client.loop_start()


    if __name__ == "__main__":
        main()
        logger.info("MQTT - Listening for messages on topic '" + str(TOPIC))


if __name__ == "__main__":
    t1 = threading.Thread(target=launch_socket)
    t2 = threading.Thread(target=launch_mqtt)
    t1.start()
    t2.start()