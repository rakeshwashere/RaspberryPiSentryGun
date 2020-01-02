import cv2
import zmq
import base64
import numpy as np

class VideoStreamer:
    def __init__(self, host, port):
        context = zmq.Context()
        footage_socket = context.socket(zmq.SUB)
        footage_socket.connect('tcp://{}:{}'.format(host, port))
        footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        # footage_socket.setsockopt(zmq.CONFLATE, 1)

        self.__footage_socket = footage_socket

    def stream(self):
        while True:
            frame = self.__footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return cv2.imencode('.jpg', source)[1].tobytes()