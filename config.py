import os
import pickle

HOST = "192.168.1.236"


class PATHS:
    SERVER_CERT = os.path.join(os.path.dirname(__file__),'resources/server.crt')
    SERVER_KEY = os.path.join(os.path.dirname(__file__),'resources/server.key')
    CLIENT_CERT = os.path.join(os.path.dirname(__file__),'resources/client.crt')
    

class DATABASE:
    HOST = "detections.cdtm4kvpi8en.eu-west-2.rds.amazonaws.com"
    DATABASE = "detections"
    USER = "BPJ00SSG00"
    PASSWORD = "!:*N~ZM48>n!`aZA"


class MQT:
    BROKER_HOST = HOST
    BROKER_PORT = 1883    #AWS 1884
    CLIENT_ID = "Server"
    TOPIC = [("cycle/init", 2), ("cycle/zones", 2), ("cycle/gps", 2)]


class SOCK:
    SERVER_HOST = HOST
    SERVER_PORT = 5001
    SERVER_CERT = PATHS.SERVER_CERT
    SERVER_KEY = PATHS.SERVER_KEY
    CLIENT_CERT = PATHS.CLIENT_CERT

