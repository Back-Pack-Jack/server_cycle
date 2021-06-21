import sys
import psycopg2
import time
import datetime
import logging
from config import DB_DEVICE, DB_COLLECTED_DATA


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


class DATABASE:


    def __init__(self, data):
        self.sensors = ['SPS30', 'MICS6814', 'ZMOD4510']
        self.data = data
        if data[2] not in self.sensors:
            self.conn = self.connect(DB_DEVICE)
        else:
            self.conn = self.connect(DB_COLLECTED_DATA)


    def connect(self, db):
        conn = psycopg2.connect(
                        host = db.HOST,
                        database = db.DATABASE,
                        user = db.USER,
                        password = db.PASSWORD)
        return conn


    def sensor(self, sensor, cur):
        
        def SPS30():
            cur.execute("INSERT INTO sensor_sensiron_sps30 (uuid, datetime, pm1_0, pm2_5, pm4_0, pm10, n_pm0_5, n_pm1_0, n_pm2_5, n_pm4_0, n_pm10, pm_avg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", \
                (self.data[0], self.data[1], self.data[3]['PM1.0'], self.data[3]['PM2.5'], self.data[3]['PM4.0'], self.data[3]['PM10'], self.data[3]['N_PM0.5'], self.data[3]['N_PM1.0'], self.data[3]['N_PM2.5'], \
                    self.data[3]['N_PM4.0'], self.data[3]['N_PM10'], self.data[3]['PM_Avg']))

        def MICS6814():
            cur.execute("INSERT INTO sensor_mics_6814 (uuid, datetime, oxidising, reducing, nh3, adc) VALUES (%s, %s, %s, %s, %s, %s) ", \
                (self.data[0], self.data[1], self.data[3]['OXIDISING'], self.data[3]['REDUCING'], self.data[3]['NH3'], self.data[3]['ADC']))

        def ZMOD4510():
            cur.execute("INSERT INTO sensor_zmod_4510 (uuid, datetime, rmox_0, rmox_1, rmox_2, rmox_3, rmox_4, rmox_5, rmox_6, rmox_7, conc_03_ppb, fast_aqi, epa_aqi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", \
                (self.data[0], self.data[1], self.data[3]['Rmox[0]'], self.data[3]['Rmox[1]'], self.data[3]['Rmox[2]'], self.data[3]['Rmox[3]'], self.data[3]['Rmox[4]'], self.data[3]['Rmox[5]'], self.data[3]['Rmox[6]'], \
                    self.data[3]['Rmox[7]'], self.data[3]['O3_conc_ppb'], self.data[3]['Fast AQI'], self.data[3]['EPA AQI']))

        return exec(sensor + '()')


    def write_to_db(self):
        cur = self.conn.cursor()
        self.sensor(self.data[2], cur)
        self.conn.commit()
        logger.info("DATABASE - inserted into database")
        cur.close()
        self.conn.close()
        logger.info("DATABASE - closed connection")
