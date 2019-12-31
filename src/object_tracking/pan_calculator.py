import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class PanCalculator:
    def __init__(self, fov, image_width):
        self.__fov = fov
        self.__image_width = image_width
        self.__gradient = (fov / float(image_width))
        self.__camera_x = image_width / 2.0
        logging.info("image width is : {} gradient is: {}".format(image_width, self.__gradient))

    # in python3 division of int by another int returns a float
    # in python
    def calculate_pan_angle(self, target_x_position):

        pan_angle = (target_x_position - self.__camera_x) * self.__gradient * 0.2 * -1.0

        logging.info("the calculated pan angle for {} is {}".format(target_x_position - self.__camera_x, pan_angle))
        return  pan_angle
        


