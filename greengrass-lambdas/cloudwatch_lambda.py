import greengrasssdk
import time
import json

iot_client = greengrasssdk.client('iot-data')
cloudwatch_connector_topic = 'cloudwatch/metric/put'

def publish_metric_to_cloudwatch_connector(metric):
    metric = json.dumps(metric)
    print("Metric to be published: " + metric)
    iot_client.publish(topic=cloudwatch_connector_topic,
        payload=metric)

# publishes the cloud watch metric received in event to cloud watch
def function_handler(event, context):
    print("The event received is: " + event)
    event = json.loads(event)
    publish_metric_to_cloudwatch_connector(event['metric'])
    return
