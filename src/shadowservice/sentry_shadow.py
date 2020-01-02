from shadowservice.shadow_service import ShadowService
from config import ROOT_DIR
import threading
import os
import json

CLIENT_ID = "SentryGun"
ENDPOINT = "a3uzv8jeh0csqg-ats.iot.us-west-2.amazonaws.com"
ENDPOINT_PORT = 8883

ROOT_CA = os.path.join(ROOT_DIR, 'certs', 'root.ca.pem')
PRIVATE_KEY = os.path.join(ROOT_DIR, 'certs', 'dfbc0e3f2b.private.key')
DEVICE_CERT = os.path.join(ROOT_DIR, 'certs', 'dfbc0e3f2b.cert.pem')


class SentryShadow:
    def __init__(self):
        self.sentry_gun_shadow = ShadowService(CLIENT_ID, ENDPOINT, ENDPOINT_PORT, ROOT_CA, PRIVATE_KEY,
                                                       DEVICE_CERT)

    def get_arming(self):
        # todo make more elegant
        return self.sentry_gun_shadow.get_state().get('arming')

    def get_mode(self):
        return self.sentry_gun_shadow.get_state().get('mode')
    
    def set_mode(self, mode):
        self.sentry_gun_shadow.update_state({'mode': mode})
    
    def set_autonomous_mode(self):
        self.set_mode('AUTONOMOUS')
    
    def set_manual_mode(self):
        self.set_mode('MANUAL')
