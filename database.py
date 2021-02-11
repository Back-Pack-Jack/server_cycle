import sys
import psycopg2
import time
import datetime
import logging
from config import DATABASE

logger = logging.getLogger("DATABASE")  # Logger for this module

output_file_handler = logging.FileHandler("database.log")
stdout_handler = logging.StreamHandler(sys.stdout)

logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)

# Connect to the postgres database
def connect():
    conn = psycopg2.connect(
                    host = DATABASE.HOST,
                    database = DATABASE.DATABASE,
                    user = DATABASE.USER,
                    password = DATABASE.PASSWORD)
    return conn


def writeToDatabase(output):
    conn = connect()
    logger.info("Opened connection To Database")
    cur = conn.cursor() # Open a cursor to perform db operations
    logger.info("Created Database Cursor")
    for _, record in enumerate(output):
        cur.execute("INSERT INTO detections (id, gate, datetime, classification) VALUES (%s, %s, %s, %s) ", (record[0], record[1], datetime.datetime.fromtimestamp(record[2]), record[3]))
    logger.info("Inserted Detections Into Database")
    conn.commit()
    logger.info("Commited Detections To Database")
    cur.close()
    logger.info("Closed Cursor")
    conn.close()
    logger.info("Closed Connection")


def addDeviceToDB(output):
    conn = connect()
    logger.info("Opened connection To Database")
    cur = conn.cursor() # Open a cursor to perform db operations
    try:
        cur.execute("INSERT INTO devices (device_id, device_name) VALUES (%s, %s) ", (output, ''))
        logger.info("Inserted new device into database")
        conn.commit()
        logger.info("Commited Detections To Database")
    except:
        logger.error("Unable to add the device. UUID already exists within database")
    cur.close()
    logger.info("Closed Cursor")
    conn.close()
    logger.info("Closed Connection")

