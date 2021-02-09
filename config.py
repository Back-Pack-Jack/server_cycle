import os
import pickle

HOST = "0.0.0.0"

'''
class PATHS:
    PATH = os.path.join(os.path.dirname(__file__),'')

'''

class DATABASE:
    HOST = "detections.cdtm4kvpi8en.eu-west-2.rds.amazonaws.com"
    DATABASE = "detections"
    USER = "BPJ00SSG00"
    PASSWORD = "!:*N~ZM48>n!`aZA"


class MQT:
    BROKER_HOST = HOST
    BROKER_PORT = 1883
    CLIENT_ID = "Server"
    TOPIC = [("cycle/init", 2), ("cycle/zones", 2), ("cycle/gps", 2)]


class SOCK:
    SERVER_HOST = HOST
    SERVER_PORT = 5001
