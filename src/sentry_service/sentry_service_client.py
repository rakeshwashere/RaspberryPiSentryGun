import socket
import os
import logging
import time
import json
import sys

logging.basicConfig(format='%(asctime)s - [%(levelname)s] %(message)s', level=logging.INFO)

class SentryServiceClient:
    def __init__(self, client_id):
        self.__client_id = client_id

        if os.path.exists("/tmp/sentry_service_unix_socket"):
            client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            client.connect("/tmp/sentry_service_unix_socket")
            logging.info("Connection to Sentry Service established")
            self.__client = client
        else:
            logging.fatal("Sentry service not found")
            sys.exit(-1)


    def fire(self):
        message = self.__generate_basic_message()
        message['command'] = 'FIRE'
        self.__client.send(json.dumps(message).encode('utf-8'))
    
    def pan(self, angle):
        message = self.__generate_basic_message()
        message['command'] = 'PAN'
        message['angle'] = angle
        self.__client.send(json.dumps(message).encode('utf-8'))

    def shutdown(self):
        message = self.__generate_basic_message()
        message['command'] = 'SHUTDOWN'
        self.__client.send(json.dumps(message).encode('utf-8'))
    
    def __generate_basic_message(self):
        message = {}
        message['timestamp'] = time.time()
        message['clientId'] = self.__client_id
        return message
