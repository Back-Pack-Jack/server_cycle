# General Imports
import logging
import os
import database
import time
import threading
import sys
import ssl

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
import hashlib
from config import MQT


# Initialize Logging
logging.basicConfig(        filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d, %H:%M:%S',
                            level=logging.INFO)  # Global logging configuration

logger = logging.getLogger("SERVER")  # Logger for this module

output_file_handler = logging.FileHandler("server.log")
stdout_handler = logging.StreamHandler(sys.stdout)

logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)


def launch_socket():

    # device's IP address
    SERVER_HOST = SOCK.SERVER_HOST
    SERVER_PORT = SOCK.SERVER_PORT
    SERVER_CERT = SOCK.SERVER_CERT
    SERVER_KEY = SOCK.SERVER_KEY
    CLIENT_CERT = SOCK.CLIENT_CERT

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    context.load_verify_locations(cafile=CLIENT_CERT)


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket Object
    s.bind((SERVER_HOST, SERVER_PORT)) # Bind The Socket To Our Server Port
    s.listen(5) # Listen, allow 5 pending requests
    logger.info('SOCKET - '+ f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    BUFFER_SIZE = 4096  # Receive 4096 Bytes In Each Transmission
    SEPARATOR = "<SEPARATOR>"

    def wrappedSocket():
        while True:
            client_socket, address = s.accept()
            logger.info('SOCKET - ' + f"[+] {address} is connected.")
            try:
                conn = context.wrap_socket(client_socket, server_side=True)
                logger.info("SSL established. Peer: {}".format(conn.getpeercert()))
                return conn
            except:
                logger.error('Unauthorised Access Attempt')

            

    def main():
        # accept connection if there is any
        while True:
            conn = wrappedSocket()
            # receive the file infos
            # receive using client socket, not server socket
            received = conn.recv(BUFFER_SIZE).decode()
            logger.info('SOCKET - Recieved Buffer Size of {}'.format(received))
            filename, filesize = received.split(SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            # convert to integer
            filesize = int(filesize)


            # start receiving the file from the socket
            # and writing to the file stream
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=BUFFER_SIZE)

            buffer = bytearray(b'')
            while True:
                try:
                    for _ in progress:
                        # read 4096 bytes from the socket (receive)
                        bytes_read = conn.recv(BUFFER_SIZE)
                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done
                            logger.info('SOCKET - Completed Transfer Of Information')
                            break
                        # write to the file the bytes we just received
                        #f.write(bytes_read)
                        buffer.append(bytes_read)
                        logger.info('SOCKET - Recieving...')
                        # update the progress bar
                        progress.update(len(bytes_read))
                finally:
                    buffer = bytes(buffer)
                    output = pickle.loads(buffer)
                    database.writeToDatabase(output)
                    #conn.shutdown(socket.SHUT_RDWR)
                    #logger.info("SOCKET - Shutdown Client Socket")
                    conn.shutdown(socket.SHUT_WR)
                    conn.close()
                    logger.info("SOCKET - Closed Client Socket")
                    break

                
   
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