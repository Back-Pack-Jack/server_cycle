import os
import pickle

HOST = "0.0.0.0"


class PATHS:
    SERVER_CERT = os.path.join(os.path.dirname(__file__),'resources/server-cert.pem')
    SERVER_KEY = os.path.join(os.path.dirname(__file__),'resources/server-key.pem')
    CA_CERT = os.path.join(os.path.dirname(__file__),'resources/ca-cert.pem')
    

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
    TOPIC = [("sensors/#", 1), ("img/#", 1), ("init/#", 1), ("object_types/#", 1)]


class SOCK:
    SERVER_HOST = HOST
    SERVER_PORT = 5002
    SERVER_CERT = PATHS.SERVER_CERT
    SERVER_KEY = PATHS.SERVER_KEY
    CA_CERT = PATHS.CA_CERT

