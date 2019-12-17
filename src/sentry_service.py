import multiprocessing
import threading
from threading import Thread
import RPi.GPIO as GPIO
import logging
import time
from sentry_controller import SentryController

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class SentryService(threading.Thread):

    def __init__(self, task_queue):
        Thread.__init__(self)
        GPIO.setmode(GPIO.BOARD)

        self.sentry_controller = SentryController()
        self.task_queue = task_queue

    def run(self):
        proc_name = self.name
        while True:
            if len(self.task_queue) == 0:
                continue
            current_task = self.task_queue.pop()
            if current_task.operation == 'FIRE':
                print("fire in the hole !!!")
                self.sentry_controller.fire()
            elif current_task.operation == 'SHUTDOWN':
                print("Shutting down!!!")
                self.sentry_controller.shutdown()
                break
            print('%s: %s' % (proc_name, current_task))
        return

    def do(self, task):
        self.task_queue.append(task)


class Task(object):
    def __init__(self, operation):
        self.operation = operation

    def __str__(self):
        return "Task is to : {0}".format(self.operation)
