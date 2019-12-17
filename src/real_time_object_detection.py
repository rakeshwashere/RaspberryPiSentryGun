from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
from collections import deque
import argparse
from threading import Thread
import imutils
import logging
import time
import os
import cv2
from sentry_controller import SentryController
from sentry_service import SentryService, Task
from shadowservice.sentry_shadow import SentryShadow
import multiprocessing
import RPi.GPIO as GPIO

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

sentry_shadow = SentryShadow()

sentry_tasks_queue = deque(maxlen=1)
sentry_service = SentryService(sentry_tasks_queue)
sentry_service.daemon = True
sentry_service.start()

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter weak detections")

args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
logging.info("loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
logging.info("starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

HEADED = True if os.getenv('DISPLAY') else False

FRAME_WIDTH = 500
FRAME_CENTER_X = FRAME_CENTER_Y = int(FRAME_WIDTH / 2)


def get_person_center_coordinates(start_x, start_y, end_x, end_y):
    center_x = (start_x + end_x) / 2
    center_y = (start_y + end_y) / 2
    return center_x, center_y


def get_cross_hair_box_coordinates(frame_width):
    frame_centerX = frame_centerY = frame_width / 2

    box_side_len = (frame_width * 0.30) / 2

    box_startX = int(frame_centerX - box_side_len)
    box_endX = int(frame_centerX + box_side_len)
    box_startY = int(frame_centerY - box_side_len)
    box_endY = int(frame_centerY + box_side_len)

    return [(box_startX, box_startY), (box_endX, box_endY)]


def draw_cross_hair_box(cv2, frame, box_coordinates):
    cv2.rectangle(frame, box_coordinates[0],
                  box_coordinates[1], (0, 0, 255), 1)


def should_fire(person_center_coordinates, cross_hair_box):
    arming = sentry_shadow.get_arming()

    if arming != 'armed':
        logging.info("Disarmed won't fire")
        return False

    box_start_x, box_start_y = cross_hair_box[0]
    box_end_x, box_end_y = cross_hair_box[1]

    person_center_x, person_center_y = person_center_coordinates

    if box_start_x > person_center_x or box_end_x < person_center_x:
        return False
    if box_start_y > person_center_y or box_end_y < person_center_y:
        return False

    logging.info("PHEW PHEW PHEW")
    return True


cross_hair_box_coordinates = get_cross_hair_box_coordinates(FRAME_WIDTH)

# loop over the frames from the video stream
while True:
    try:
        start_time = time.time()
        # grab the frame from the threaded video stream and resize it
        frame = vs.read()
        frame = imutils.resize(frame, width=FRAME_WIDTH)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # sentry_controller.fire()
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                object_detected = CLASSES[idx]
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)

                if object_detected == "person":
                    person_center_coordinates = get_person_center_coordinates(
                        startX, startY, endX, endY)

                    cv2.putText(frame, "Person detected", (10, 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                    cv2.rectangle(frame, (startX, startY),
                                  (endX, endY), COLORS[idx], 2)

                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

                    if should_fire(person_center_coordinates, cross_hair_box_coordinates):
                        sentry_service.do(Task('FIRE'))
                        cv2.putText(frame, "PHEW PHEW !!!", (FRAME_CENTER_X - 30,
                                                             FRAME_CENTER_Y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (255, 100, 0),
                                    2)
                    break

        draw_cross_hair_box(cv2, frame, cross_hair_box_coordinates)

        if HEADED:
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                sentry_service.do(Task('SHUTDOWN'))
                break
        
        # update the FPS counter
        fps.update()

        logging.info("Frame processed in: %s", time.time() - start_time)

    except Exception as ex: 
        sentry_service.do(Task('SHUTDOWN'))
        sentry_service.join()
        # print("Exception caught: " + str(ex))
        raise ex

sentry_service.do(Task('SHUTDOWN'))
sentry_service.join()
# stop the timer and display FPS information
fps.stop()
GPIO.cleanup()

if HEADED:
    # do a bit of cleanup
    cv2.destroyAllWindows()
vs.stop()
logging.info(" elapsed time: {:.2f}".format(fps.elapsed()))
logging.info(" approx. FPS: {:.2f}".format(fps.fps()))





