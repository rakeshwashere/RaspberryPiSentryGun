from config import ROOT_DIR
import os

class IoTCoreConstants:
    THING_NAME = "SentryGun"
    IOT_CORE_ENDPOINT = "a3uzv8jeh0csqg-ats.iot.us-west-2.amazonaws.com"

    ROOT_CA = os.path.join(ROOT_DIR, 'certs', 'root.ca.pem')
    PRIVATE_KEY = os.path.join(ROOT_DIR, 'certs', 'dfbc0e3f2b.private.key')
    DEVICE_CERT = os.path.join(ROOT_DIR, 'certs', 'dfbc0e3f2b.cert.pem')