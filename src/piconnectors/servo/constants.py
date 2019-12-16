class ServoConstants:
    OFFSET_DUTY = 0.0  # define pulse offset of servo
    # define pulse duty cycle for minimum angle of servo
    SERVO_MIN_DUTY = 2.0 + OFFSET_DUTY
    # define pulse duty cycle for maximum angle of servo
    SERVO_MAX_DUTY = 12.0 + OFFSET_DUTY

    PWM_FREQUENCY = 50
    POWER_PIN = 12
    TRIGGER_PIN = 36

