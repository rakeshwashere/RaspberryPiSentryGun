from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from config import ROOT_DIR
import time
import json
import os
import logging

class ShadowServiceListener:
    def __init__(self, clientId, endpoint, endpoint_port, root_ca, private_key, device_cert):
        self.clientId = clientId
        self.endpoint = endpoint
        self.endpoint_port = endpoint_port
        self.root_ca = root_ca
        self.private_key = private_key
        self.device_cert = device_cert

        #initalize shadow client
        self.shadow_client = AWSIoTMQTTShadowClient(self.clientId)
        self.shadow_client.configureEndpoint(self.endpoint, self.endpoint_port)
        self.shadow_client.configureCredentials(self.root_ca, self.private_key, self.device_cert)

        # For Websocket, we only need to configure the root CA
        # myShadowClient.configureCredentials("YOUR/ROOT/CA/PATH")
        self.shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.shadow_client.configureMQTTOperationTimeout(5)  # 5 sec

        self.shadow_client.connect()
        # Create a device shadow instance using persistent subscription

        self.device_shadow = self.shadow_client.createShadowHandlerWithName(clientId, True)
        # shadowCallbackContainer_Bot = ShadowCallbackContainer(self.device_shadow)


   

    # class ShadowCallbackContainer:
    #     def __init__(self, deviceShadowInstance):
    #         self.deviceShadowInstance = deviceShadowInstance

    #     # Custom Shadow callback
    #     def customShadowCallback_Delta(self, payload, responseStatus, token):
    #         # payload is a JSON string ready to be parsed using json.loads(...)
    #         # in both Py2.x and Py3.x
    #         print("Received a delta message:")
    #         payloadDict = json.loads(payload)
    #         deltaMessage = payloadDict["state"]
    #         print(deltaMessage)
    #         print(str(deltaMessage["status"]))
    #         print("Request to update the reported state...")
    #         newPayload = '{"state":{"reported":' + json.dumps(deltaMessage) + '}}'
    #         self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)

    #         if deltaMessage["status"] and sentry_gun_status_change_handler:
    #             print("Informing sentry gun about status change")
    #             sentry_gun_status_change_handler(deltaMessage["status"])

    #         print("Sent.")


    

    # def customCallback(client, userdata, message):
    #     print("Received a message on MQTT")
    #     print("client  " + json.dumps(client, sort_keys=True, indent=4))
    #     print("message is " + json.dumps(message, sort_keys=True, indent=4))
    #     print("userdata is " + json.dumps(userdata, sort_keys=True, indent=4))


    # Shadow operations
    # device_shadow.shadowGet(customCallback, 5)
    # device_shadow.shadowUpdate(myJSONPayload, customCallback, 5)

    # Listen on deltas
    # device_shadow.shadowRegisterDeltaCallback(
    #     shadowCallbackContainer_Bot.customShadowCallback_Delta)

    def get_shadow(self, customCallback):
        self.device_shadow.shadowGet(customCallback, 5)

    def register_shadow_delta_handler(self, callback):
        print("Registering shadow delta handler")
        self.shadow_delta_handler = callback

    # Keep the process alive to listen for messages.
    def listen():
        print("starting shadown service listener")
        while True:
            time.sleep(1)
