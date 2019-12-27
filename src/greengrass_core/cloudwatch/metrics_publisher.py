import json


class MetricsPublisher:
    def __init__(self, core_mqtt_client, metrics_publishing_topic):
        self.__core_mqtt_client = core_mqtt_client
        self.__metrics_publishing_topic = metrics_publishing_topic

    def publish_metric(self, metric):
        message = {}
        message['metric'] = metric
        messageJson = json.dumps(message)

        self.__core_mqtt_client.publish(
            self.__metrics_publishing_topic, json.dumps(messageJson), 0)
