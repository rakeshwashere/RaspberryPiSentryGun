import multiprocessing
import threading
from threading import Thread
import traceback
import RPi.GPIO as GPIO
import logging
import time
from sentry_service import SentryController
import socket
import os
import os.path
import time
import json
import signal
import sys

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

GPIO.setmode(GPIO.BOARD)
sentry_controller = SentryController()

# handle termination gracefully
def sigterm_handler(signum, frame):
    logging.info("Signal to terminate received")
    shutdown_sentry_service()

signal.signal(signal.SIGTERM, sigterm_handler)

if os.path.exists("/tmp/sentry_service_unix_socket"):
    os.remove("/tmp/sentry_service_unix_socket")

logging.info("Opening socket...")

server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
server.bind("/tmp/sentry_service_unix_socket")

last_fire_time = 0

def shutdown_sentry_service():
    sentry_controller.shutdown()
    server.close()
    os.remove("/tmp/sentry_service_unix_socket")
    logging.info("Shutdown sentry controller, cleaned up, Shutting down...")
    sys.exit()

logging.info("Listening...")
while True:
    try:
        datagram = server.recv(1024)
        datagram = datagram.decode('utf-8')
        logging.info("recevied message from client %s", datagram)

        message = json.loads(datagram)
        command = message['command']

        if not datagram:
            break
        elif "FIRE" == command and message['timestamp'] >  (last_fire_time + 3.8): 
            last_fire_time = time.time()
            logging.info("matched fire again for command sent at %s", message['timestamp'])
            sentry_controller.fire()
        elif "SET_PAN_ANGLE" == command:
            pan_angle = message['angle']
            logging.info("Set pan servo to angle: {}".format(pan_angle))
            sentry_controller.pan(pan_angle)
        elif "PAN_RIGHT" == command:
            angle = message.get('angle')
            logging.info("Panning to the right by angle: {}".format(angle))
            sentry_controller.pan_right(angle)
        elif "PAN_LEFT" == command:
            angle = message.get('angle')
            logging.info("Panning to the left by angle: {}".format(angle))
            sentry_controller.pan_left(angle)
        else:
            if "SHUTDOWN" == message['command']:
                shutdown_sentry_service()
    except Exception as e:
        logging.error("Exception raised: {} ".format(e))
        traceback.print_exc(file=sys.stdout)
class Task(object):
    def __init__(self, operation):
        self.operation = operation

    def __str__(self):
        return "Task is to : {0}".format(self.operation)