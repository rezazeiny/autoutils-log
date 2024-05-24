import logging
import sys

import requests

from .base import BaseLogHandler


class LogstashHandler(BaseLogHandler):
    """
        A handler class which send data to logstash.
    """

    def __init__(self, log_server: str, app_name: str = None, host_name: str = None, extra_data: dict = None):
        super().__init__(app_name=app_name, host_name=host_name, extra_data=extra_data)
        self.log_server = log_server

    def send(self, send_data: dict):
        if not self.log_server:
            return
        urllib3_log = logging.getLogger("urllib3")
        urllib3_log.setLevel(logging.CRITICAL)
        urllib3_log.propagate = False
        headers = {"Content-Type": "application/json"}
        requests.post(self.log_server, json=send_data, headers=headers)

    def emit(self, record: logging.LogRecord) -> None:
        if not self.log_server:
            return
        send_data = None
        try:
            send_data = self._get_send_data(record=record)
            self.send(send_data=send_data)

        except RecursionError:  # See issue 36272
            raise
        except Exception as e:
            if sys.stderr:
                sys.stderr.write(f"error in send to logstash {self.log_server}. e: {e}, send_data: {send_data}")
