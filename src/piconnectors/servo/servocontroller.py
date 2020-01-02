import RPi.GPIO as GPIO
import time
from piconnectors.servo.constants import ServoConstants
from piconnectors.utils import Utils


def map_angle_to_cycle(value, from_low, from_high, to_low, to_high):
    return (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low

def wait_for_servo_to_move(angle):
    print("sleeping for angle {} for {} seconds ".format(angle, (0.2/60) * angle))
    time.sleep((0.2/60) * angle) # 0.2 seconds to move 60 degrees, based on datasheet for servo model MG995

class ServoController:
    def __init__(self, pin):
        Utils.validate_pi_setup()
        self.pin = pin
        # setup servo
        GPIO.setup(pin, GPIO.OUT)  # Set pin mode is output
        GPIO.output(pin, GPIO.LOW)
        self.servo = GPIO.PWM(
            pin, ServoConstants.PWM_FREQUENCY)  # set Frequency
        self.servo.start(0)

    def rest_servo(self):
        self.servo.start(0)

    def set_angle(self, angle, **kwargs):  # make the servo rotate to specific angle (0-180 degrees)

        print("setting angle " + str(angle))
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180

        # map the angle to duty cycle and output it
        self.servo.ChangeDutyCycle(
            map_angle_to_cycle(angle, 0, 180, ServoConstants.SERVO_MIN_DUTY, ServoConstants.SERVO_MAX_DUTY))

        sleep_for = kwargs.get('sleep_for', None)
        reset_servo = kwargs.get('reset_servo', True)
        if not sleep_for:
            wait_for_servo_to_move(angle)
        else:
            time.sleep(sleep_for)
        
        if reset_servo:
            self.rest_servo() # hack to stop servo jitter
        # TODO set sleep time based on angle of rotation

    def stop(self):
        self.rest_servo()
    def destroy(self):
        self.servo.stop()