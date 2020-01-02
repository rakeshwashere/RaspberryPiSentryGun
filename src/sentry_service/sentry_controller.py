import time

from piconnectors.servo.constants import ServoConstants
from piconnectors.servo.servocontroller import ServoController
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
class SentryController:
    def __init__(self):
        self.power_servo = ServoController(ServoConstants.POWER_PIN)
        self.trigger_servo = ServoController(ServoConstants.TRIGGER_PIN)
        self.pan_servo = ServoController(ServoConstants.PAN_PIN)
        self.__current_pan_servo_angle = 90

    #angle must be between 0 and 180
    def __record_pan_angle(self, angle):
        self.__current_pan_servo_angle = min(max(angle, 0), 180)
        logging.info("Updated sentry pan angle to {}".format(self.__current_pan_servo_angle))

    def __power_up(self):
        self.power_servo.set_angle(60.0, sleep_for=1.6, reset_servo=False)

    def __power_down(self):
        self.power_servo.set_angle(30.0, sleep_for=0.3)

    def __pull_trigger(self):
        self.trigger_servo.set_angle(180.0, sleep_for=1.2)

    def __release_trigger(self):
        self.trigger_servo.set_angle(0.0, sleep_for=1.0)

    def __pan(self, angle):
        self.pan_servo.set_angle(angle, sleep_for=1.0)

    def fire(self):
        self.__power_up()
        self.__pull_trigger()
        self.__release_trigger()
        self.__power_down()

    # todo replace with decorator
    def pan(self, angle):
        logging.info("Previous pan servo angle: {}, updating to : {}".format(self.__current_pan_servo_angle, angle))
        self.pan_servo.set_angle(angle)
        self.__record_pan_angle(angle)
    
    def pan_right(self, angle):
        # self.__record_pan_angle(angle * -1.0) 
        self.pan(self.__current_pan_servo_angle - angle)

    def pan_left(self, angle):
        # self.__record_pan_angle(angle) 
        self.pan(self.__current_pan_servo_angle + angle)
        
    def standby(self):
        self.__power_down()
        self.__release_trigger()

    def shutdown(self):
        self.__release_trigger()
        self.__power_down()
        self.power_servo.destroy()
        self.trigger_servo.destroy()
