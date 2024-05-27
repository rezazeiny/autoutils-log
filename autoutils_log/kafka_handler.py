import datetime
import json
import logging
import sys

import pytz
from confluent_kafka import Producer

from .base import BaseLogHandler


class KafkaHandler(BaseLogHandler):
    """
        A handler class which send data to logstash.
    """

    def __init__(self, log_server: str, topic: str, app_name: str = None, host_name: str = None,
                 extra_data: dict = None, timeout: int = 2,
                 timezone: str = "Asia/Tehran"):
        super().__init__(app_name=app_name, host_name=host_name, extra_data=extra_data)
        self.log_server = log_server
        self.timezone = timezone
        self.topic = topic
        self.timeout = timeout
        self.producer = Producer({'bootstrap.servers': self.log_server}) if self.log_server else None

    def _get_send_data(self, record: logging.LogRecord):
        send_data = super()._get_send_data(record=record)
        send_data["time"] = self.get_now_time_for_elastic()
        return send_data

    def send(self, send_data: dict):
        if self.producer is None:
            return
        self.producer.produce(self.topic, json.dumps(send_data).encode("utf-8"))
        self.producer.flush(timeout=self.timeout)

    def emit(self, record: logging.LogRecord) -> None:
        if not self.log_server or not self.topic:
            return
        try:
            send_data = self._get_send_data(record=record)
            self.send(send_data=send_data)
        except RecursionError:  # See issue 36272
            raise
        except Exception as e:
            if sys.stderr:
                sys.stderr.write(f"error in send to kafka {self.log_server}. e: {e}")

    def get_now_time_for_elastic(self):
        tz = pytz.timezone(self.timezone)
        return datetime.datetime.now(tz=tz).strftime("%Y-%m-%dT%H:%M:%S%z")
