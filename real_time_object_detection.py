# USAGE
# python3 real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt
# --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import greengrasssdk
import platform

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

prototxt = 'MobileNetSSD_deploy.prototxt.txt'
model = 'MobileNetSSD_deploy.caffemodel'
confidence_threshold = 0.2

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

FRAME_WIDTH = 500
FRAME_CENTERX = FRAME_CENTERY = int(FRAME_WIDTH/2)

humans_killed = 0


def is_running_in_lambda():
    if os.getenv('AWS_EXECUTION_ENV'):
        return True


def get_person_center_coordinates(startX, startY, endX, endY):
    centerX = (startX + endX)/2
    centerY = (startY + endY)/2
    return (centerX, centerY)


def get_cross_hair_box_coordinates(frame_width):
    frame_centerX = frame_centerY = frame_width/2

    box_side_len = (frame_width * 0.30)/2

    box_startX = int(frame_centerX - box_side_len)
    box_endX = int(frame_centerX + box_side_len)
    box_startY = int(frame_centerY - box_side_len)
    box_endY = int(frame_centerY + box_side_len)

    return [(box_startX, box_startY), (box_endX, box_endY)]


def draw_cross_hair_box(cv2, frame, box_coordinates):
    cv2.rectangle(frame, box_coordinates[0],
                  box_coordinates[1], (0, 0, 255), 1)


def should_fire(person_center_coordinates, cross_hair_box):
    box_startX, box_startY = cross_hair_box[0]
    box_endX, box_endY = cross_hair_box[1]

    person_centerX, person_centerY = person_center_coordinates

    if box_startX > person_centerX or box_endX < person_centerX:
        return False
    if box_startY > person_centerY or box_endY < person_centerY:
        return False

        print("[INFO] human found must destroy #" + str(humans_killed))
        client.publish(
            topic='hello/person',
            queueFullPolicy='AllOrException',
            payload='human detected must destroy !!!')

        humans_killed = humans_killed + 1

    return True


cross_hair_box_coordinates = get_cross_hair_box_coordinates(FRAME_WIDTH)

# TODO make this more OO
# TODO It could be headless even when not running in lambda figure out a better way to check if device has display

#HEADLESS = is_running_in_lambda()
HEADLESS = True


def perform_object_detection():

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    fps = FPS().start()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
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

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > confidence_threshold:
                # extract the index of the claass label from the
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

                    if not HEADLESS:
                        cv2.putText(frame, "Person detected", (10, 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                        cv2.rectangle(frame, (startX, startY),
                                      (endX, endY), COLORS[idx], 2)

                        y = startY - 15 if startY - 15 > 15 else startY + 15
                        cv2.putText(frame, label, (startX, y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

                    if should_fire(person_center_coordinates, cross_hair_box_coordinates):
                        cv2.putText(frame, "PHEW PHEW !!!", (FRAME_CENTERX - 30,
                                                             FRAME_CENTERY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 2)

        draw_cross_hair_box(cv2, frame, cross_hair_box_coordinates)

        # show the output frame if there is a display
        if not HEADLESS:
            cv2.imshow("Frame", frame)

            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()

    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    if not HEADLESS:
        cv2.destroyAllWindows()
    vs.stop()


if __name__ == "__main__":
    perform_object_detection()
