import sys
import psycopg2
import time
import datetime
import logging
from config import DATABASE

'''
logger = logging.getLogger("DATABASE")  # Logger for this module

output_file_handler = logging.FileHandler("database.log")
stdout_handler = logging.StreamHandler(sys.stdout)

logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)
'''

# --- AWS Logging
logging.basicConfig(        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d, %H:%M:%S',
                            level=logging.INFO)
logger = logging.getLogger()


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
    logger.info("DATABASE - Opened connection To Database")
    cur = conn.cursor() # Open a cursor to perform db operations
    logger.info("DATABASE - Created Database Cursor")
    #add try statement to flag records that are incorrect along with the device for debugging
    for _, record in enumerate(output):
        if len(record) <=4:
            cur.execute("DATABASE - INSERT INTO detections (id, gate, datetime, classification) VALUES (%s, %s, %s, %s) ", (record[0], record[1], datetime.datetime.fromtimestamp(record[2]), record[3])) # Temp Fix
    logger.info("DATABASE - Inserted Detections Into Database")
    conn.commit()
    logger.info("DATABASE - Commited Detections To Database")
    cur.close()
    logger.info("DATABASE - Closed Cursor")
    conn.close()
    logger.info("DATABASE - Closed Connection")


def addDeviceToDB(output):
    conn = connect()
    logger.info("DATABASE - Opened connection To Database")
    cur = conn.cursor() # Open a cursor to perform db operations
    try:
        cur.execute("DATABASE - INSERT INTO devices (device_id, device_name) VALUES (%s, %s) ", (output, ''))
        logger.info("DATABASE - Inserted new device into database")
        conn.commit()
        logger.info("DATABASE - Commited Detections To Database")
    except:
        logger.error("DATABASE - Unable to add the device. UUID already exists within database")
    cur.close()
    logger.info("DATABASE - Closed Cursor")
    conn.close()
    logger.info("DATABASE - Closed Connection")