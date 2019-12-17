from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from config import ROOT_DIR
import time
import json
import os
import logging

class ShadowService:
    def __init__(self, clientId, endpoint, endpoint_port, root_ca, private_key, device_cert):
        self.clientId = clientId
        self.endpoint = endpoint
        self.endpoint_port = endpoint_port
        self.root_ca = root_ca
        self.private_key = private_key
        self.device_cert = device_cert
        self.state = {}

        # initalize shadow client
        self.shadow_client = AWSIoTMQTTShadowClient(self.clientId)
        self.shadow_client.configureEndpoint(self.endpoint, self.endpoint_port)
        self.shadow_client.configureCredentials(
            self.root_ca, self.private_key, self.device_cert)

        # For Websocket, we only need to configure the root CA
        # myShadowClient.configureCredentials("YOUR/ROOT/CA/PATH")
        self.shadow_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.shadow_client.configureMQTTOperationTimeout(5)  # 5 sec

        self.shadow_client.connect()
        # Create a device shadow instance using persistent subscription

        self.device_shadow = self.shadow_client.createShadowHandlerWithName(
            clientId, True)
     
        # Shadow operations
        self.device_shadow.shadowGet(self.__get_shadow_callback, 5)
        # device_shadow.shadowUpdate(myJSONPayload, customCallback, 5)

        # Listen on deltas
        self.device_shadow.shadowRegisterDeltaCallback(self.__shadow_delta_callback)

    def __get_shadow_callback(self, userdata, client, message):

        userdata = json.loads(userdata)
        print("Received device shadow state")
        # print("client  " + json.dumps(client, sort_keys=True, indent=4))
        # print("message is " + json.dumps(message, sort_keys=True, indent=4))
        # print("userdata is " + json.dumps(userdata, sort_keys=True, indent=4))
        state = userdata["state"]["desired"]
        self.__acknowledge_state(state)
        self.state = state
        print("state of shadow is " + str(state))

    def __shadow_delta_callback(self, payload, responseStatus, token):
        print("Received a delta message:")
        payloadDict = json.loads(payload)
        deltaMessage = payloadDict["state"]

        print(deltaMessage)
        print("Request to update the reported state...")
        self.__acknowledge_state(deltaMessage)
        self.state.update(deltaMessage)
        print("state of shadow is " + str(self.state))

    def __acknowledge_state(self, acknowledgedState):
        payload = '{"state":{"reported":' + \
            json.dumps(acknowledgedState) + '}}'
        self.device_shadow.shadowUpdate(payload, None, 5)
        print("Acknolwedged state")

    def get_state(self):
        return self.state