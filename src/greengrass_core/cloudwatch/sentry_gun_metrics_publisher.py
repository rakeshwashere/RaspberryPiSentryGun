import time


def create_request_with_all_fields(metric_name, value, unit):
    return {
        "request": {
            "namespace": "SentryGun",
            "metricData": {
                "metricName": metric_name,
                "dimensions": [
                    {
                        "name": "test",
                        "value": "test"
                    }
                ],
                "value": value,
                "unit": unit,
                "timestamp": time.time()
            }
        }
    }

class SentryGunMetricsPublisher:
    def __init__(self, metrics_publisher):
        self.__metrics_publisher = metrics_publisher

    def publish_frame_processing_time(self, latency):
        metric = create_request_with_all_fields(
            "FrameProcessingTime", latency, 'Seconds')
        self.__metrics_publisher.publish_metric(metric)

    def publish_fire_event(self):
        metric = create_request_with_all_fields(
            "FireEvent", 1, 'Count')
        self.__metrics_publisher.publish_metric(metric)

    def publish_person_detection_event(self):
        metric = create_request_with_all_fields(
            "PersonDetectionEvent", 1, 'Count')
        self.__metrics_publisher.publish_metric(metric)
