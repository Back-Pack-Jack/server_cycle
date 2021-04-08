import sys
import psycopg2
import time
import datetime
import logging
from config import DATABASE
import pickle

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

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# Connect to the postgres database
def connect():
    conn = psycopg2.connect(
                    host = DATABASE.HOST,
                    database = DATABASE.DATABASE,
                    user = DATABASE.USER,
                    password = DATABASE.PASSWORD)
    return conn


def dispatch(ID, TIME, TOPIC, DATA, cur):
    def cycle_img():
        cur.execute("INSERT INTO device_imgs (uuid, img, date, time) VALUES (%s, %s, %s, %s) ", 
        (ID, pickle.dumps(DATA), TIME.split()[0], TIME.split()[1]))
    def cycle_gps():
        pass
    def cycle_bme680():
        pass
    def cycle_sensiron():
        pass
    def cycle_new_device():
        cur.execute("INSERT INTO devices (device_id, date, time) VALUES (%s, %s, %s) ", 
        (ID, TIME.split()[0], TIME.split()[1]))
    def cycle_counts():
        cur.execute("INSERT INTO detections (id, gate, datetime, classification) VALUES (%s, %s, %s, %s) ", 
        (DATA[0], DATA[1], datetime.datetime.fromtimestamp(DATA[2]), DATA[3]))
    def cycle_livestream():
        pass

    dispatcher = {
            "cycle/img" :       [cycle_img],
            "cycle/gps" :       ['handle_gps'],
            "cycle/bme680" :    ['handle_bme680'],
            "cycle/sensiron" :  ['handle_sensiron'],
            "cycle/newdevice" : [cycle_new_device],
            "cycle/counts" :    [cycle_counts],
            "cycle/livestream" :['handle_livestream']
            }    
    
    for f in dispatcher[TOPIC]:
        return f() 


def write_to_db(ID, TOPIC, DATA, TIME=now):

    conn = connect()
    logger.info("[+] DATABASE - Opened connection To Database")
    cur = conn.cursor() # Open a cursor to perform db operations
    logger.debug("[+] DATABASE - Created Database Cursor")
    dispatch(ID, TIME, TOPIC, DATA, cur)
    conn.commit()
    logger.info(f"[+] DATABASE - Inserted {TOPIC.split('/')[1].capitalize()} Into Database")
    cur.close()
    logger.debug(f"[+] DATABASE - Closed Cursor")
    conn.close()
    logger.info(f"[+] DATABASE - Closed Connection")

class MSG_HANDLER:
    def __init__(self, _id, msg, _sr):
        self.id = _id
        self.query = msg
        self.snd_rcv = _sr
        self.data = None
        self.time = None
        self.dispatcher = {
            "cycle/newdevice" : ["TBC"],
            "cycle/img" : ["TBC"]
            }

    def perform_request(self, func_list):
        
        def create_packet():
            self.time = now
            packet = {
                        "ID" : self.id,
                        "TIME" : self.time,
                        "TOPIC" : self.query,
                        "DATA" : self.data
                    }
            return(packet)


        def form_data():
            if self.snd_rcv == "S":
                for f in func_list:
                    try:
                        self.data = f()
                    except Exception:
                        self.data = f
            elif self.snd_rcv == "R":
                self.data = None

        
        def snd_packet():  
                form_data()       
                packet = create_packet()
                return packet
            
        packet = snd_packet()
        return packet


    # Reads in an MQTT topic and performs an action based upon pre-determined dispatcher functions,
    # returning the data back to the create_response function as data.
    def handle_request(self):
        packet = self.perform_request(self.dispatcher[self.query]) 
        return packet