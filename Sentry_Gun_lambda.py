from real_time_object_detection import perform_object_detection
import greengrasssdk
import time
client = greengrasssdk.client('iot-data')

counter = 0
# while counter < 10:
#     client.publish(
#         topic='hello/world',
#         queueFullPolicy='AllOrException',
#         payload='Hello world! Sent from Sentry gun GG core lambda PHEW !!! PHEW !!!')
#     counter = counter + 1    
#     time.sleep(2)

perform_object_detection()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
