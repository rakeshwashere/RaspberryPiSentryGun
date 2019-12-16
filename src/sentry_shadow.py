from shadowservice import ShadowServiceListener
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
        self.sentry_gun_shadow = ShadowServiceListener(CLIENT_ID, ENDPOINT, ENDPOINT_PORT, ROOT_CA, PRIVATE_KEY,
                                                       DEVICE_CERT)
        self.sentry_gun_shadow_listener = threading.Thread(target=self.sentry_gun_shadow.listen, args=(), daemon=True)
        self.sentry_gun_shadow.register_shadow_delta_handler(self.shadow_delta_handler)

    # this should be synchronous
    def get_status(self):
        self.sentry_gun_shadow.get_shadow(self.__get_shadow_callback)
        print("called get_status in sentry shadow")
        return self.status

    def get_ammo_status(self):
        return self.ammo_status

    def update_status(self):
        pass

    def update_ammo_status(self):
        pass

    def shadow_delta_handler(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x
        print("Received a delta message:")
        payload_dict = json.loads(payload)
        delta_message = payload_dict["state"]
        print(delta_message)
        print(str(delta_message["status"]))
        print("Request to update the reported state...")
        new_payload = '{"state":{"reported":' + json.dumps(delta_message) + '}}'
        self.deviceShadowInstance.shadowUpdate(new_payload, None, 5)

        if delta_message["status"]:
            print("Informing sentry gun about status change")
            sentry_gun_status_change_handler(delta_message["status"])

        print("Sent.")

    def __get_shadow_callback(self, client, userdata, message):
        print("Received a message on MQTT")
        print("client  " + json.dumps(client, sort_keys=True, indent=4))
        print("message is " + json.dumps(message, sort_keys=True, indent=4))
        print("userdata is " + json.dumps(userdata, sort_keys=True, indent=4))
