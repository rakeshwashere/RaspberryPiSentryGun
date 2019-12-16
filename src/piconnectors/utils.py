from RPi import GPIO


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def validate_pi_setup():
        if GPIO.getmode() == -1:
            raise Exception('Pi GPIO mode not set, needs to be set to GPIO.BCM or GPIO.BOARD')
