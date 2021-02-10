import psycopg2
import time
import datetime
import logging
from config import DATABASE

logger = logging.getLogger("DATABASE")  # Logger for this module

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
    cur = conn.cursor() # Open a cursor to perform db operations
    for _, record in enumerate(output):
        cur.execute("INSERT INTO detections (id, gate, datetime, classification) VALUES (%s, %s, %s, %s) ", (record[0], record[1], datetime.datetime.fromtimestamp(record[2]), record[3]))
    logger.info("Inserted detections into database")
    conn.commit()
    cur.close()
    conn.close()


def addDeviceToDB(output):
    conn = connect()
    cur = conn.cursor() # Open a cursor to perform db operations
    try:
        cur.execute("INSERT INTO devices (device_id, device_name) VALUES (%s, %s) ", (output, ''))
        logger.info("Inserted new device into database")
        conn.commit()
    except:
        logger.error("Unable to add the device. UUID already exists within database")
    cur.close()
    conn.close()

