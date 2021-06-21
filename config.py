import os
import pickle

HOST = "0.0.0.0"


class PATHS:
    SERVER_CERT = os.path.join(os.path.dirname(__file__),'resources/server.crt')
    SERVER_KEY = os.path.join(os.path.dirname(__file__),'resources/server.key')
    CLIENT_CERT = os.path.join(os.path.dirname(__file__),'resources/client.crt')
    

class DB_DEVICE:
    HOST = "db-device.ctqynr3zk10q.eu-west-2.rds.amazonaws.com"
    DATABASE = "postgres"
    USER = "SSG_Mob"
    PASSWORD = "$Zz]=(Bg{!2<FVzA"


class DB_COLLECTED_DATA:
    HOST = "db-collected-data.ctqynr3zk10q.eu-west-2.rds.amazonaws.com"
    DATABASE = "postgres"
    USER = "SSG_Mob"
    PASSWORD = "yd>$C(X-99TFgmYP"


class MQT:
    BROKER_HOST = HOST
    BROKER_PORT = 1884
    CLIENT_ID = "Server"
    TOPIC = [("sensors/#", 1)]


class SOCK:
    SERVER_HOST = HOST
    SERVER_PORT = 5001
    SERVER_CERT = PATHS.SERVER_CERT
    SERVER_KEY = PATHS.SERVER_KEY
    CLIENT_CERT = PATHS.CLIENT_CERT

