#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from piconnectors.servo.constants import ServoConstants
from piconnectors.utils import Utils


def map_angle_to_cycle(value, from_low, from_high, to_low, to_high):
    return (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low


class ServoController:
    def __init__(self, pin):
        self.pin = pin

        Utils.validate_pi_setup()
        # setup servo
        GPIO.setup(pin, GPIO.OUT)  # Set pin mode is output
        GPIO.output(pin, GPIO.LOW)
        self.servo = GPIO.PWM(pin, ServoConstants.PWM_FREQUENCY)  # set Frequency
        self.servo.start(0)

    def set_angle(self, angle):  # make the servo rotate to specific angle (0-180 degrees)

        print("setting angle " + str(angle))
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180

        # print("Setting duty cycle to {0} for angel {1}"
        # .format((map(angle, 0, 180, ServoConstants.SERVO_MIN_DUTY, ServoConstants.SERVO_MAX_DUTY)), angle))

        # map the angle to duty cycle and output it
        self.servo.ChangeDutyCycle(
            map_angle_to_cycle(angle, 0, 180, ServoConstants.SERVO_MIN_DUTY, ServoConstants.SERVO_MAX_DUTY))

        # TODO set sleep time based on angle of rotation

    def stop(self):
        # self.servo.ChangeDutyCycle(0.0)
        pass

    def destroy(self):
        self.servo.stop()

    # def 

# def setup():
#     global p
#     GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
#     GPIO.setup(ServoConstants.POWERUP_PIN, GPIO.OUT)   # Set ServoConstants.POWERUP_PIN's mode is output
#     GPIO.output(ServoConstants.POWERUP_PIN, GPIO.LOW)  # Set ServoConstants.POWERUP_PIN to low

#     p = GPIO.PWM(ServoConstants.POWERUP_PIN, 50)     # set Frequece to 50Hz
#     p.start(0)                     # Duty Cycle = 0

# ############################
#     global trigger

#     GPIO.setup(ServoConstants.TRIGGER_PIN, GPIO.OUT)   # Set ServoConstants.POWERUP_PIN's mode is output
#     GPIO.output(ServoConstants.TRIGGER_PIN, GPIO.LOW)  # Set ServoConstants.POWERUP_PIN to low
#     trigger = GPIO.PWM(ServoConstants.TRIGGER_PIN, 50)     # set Frequece to 50Hz
#     trigger.start(0)


# def powerup():
#     # global p
#     # servoWrite(0.0, p)
#     # time.sleep(1.0)
#     servoWrite(40.0, p)
#     time.sleep(0.5)

# def powerdown():
#     # global p
#     servoWrite(30.0, p)

#     time.sleep(0.5)

# def pullTrigger():
#     # global trigger
#     servoWrite(140.0, trigger)
#     time.sleep(0.9)

# def releaseTrigger():
#     # global trigger
#     servoWrite(0.0, trigger)
#     time.sleep(0.6)

# def loop():
#     counter = 1
#     while True:
#         try:
#             # pass
#             # some code
#             # servoWrite(0.0)
#             # time.sleep(1.0)
#             # servoWrite(15.0)
#             # time.sleep(5.0)
#             # print("Using conunter value " + str(counter))
#             # p.ChangeDutyCycle(1.32)
#             # counter = counter + 0.1
#             # time.sleep(1.0)
#             # powerup()


#             pullTrigger()
#             releaseTrigger()
#         except KeyboardInterrupt:
#             print("putting into zero degree position")

#             powerdown()
#             releaseTrigger()


#             trigger.stop()
#             p.stop()
#             GPIO.cleanup()
#             break

#     # servoWrite(180.0)
#     # time.sleep(0.5)
#     # servoWrite(0.0)
#     # time.sleep(0.5)
#     # time.sleep(2)
# #     while True:
# #         for dc in range(0, 181, 1):  # make servo rotate from 0 to 180 deg
# #             servoWrite(dc)     # Write to servo
# #             time.sleep(0.001)
# #         # time.sleep(0.5)
# #         for dc in range(180, -1, -1):  # make servo rotate from 180 to 0 deg
# #             servoWrite(dc)
# #             time.sleep(0.001)
# #         # time.sleep(0.5)

# def destroy():
#     p.stop()
#     GPIO.cleanup()

# if __name__ == '__main__':  # Program start from here
#     print('Progra   m is starting...')
#     time.sleep(3)
#     setup()
#     powerdown()
#     powerup()
#     time.sleep(1)
#     # releaseTrigger()
#     try:
#         loop()
#     # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
#     except KeyboardInterrupt:
#         destroy()
