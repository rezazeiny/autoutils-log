import logging
from typing import List

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


def get_inner_detail(data_list: List[tuple], sep: str = ":"):
    """
        For remove repeat
    """
    detail = ""
    last_cond = False
    for cond, data in data_list:
        if cond:
            if last_cond:
                detail += sep
            detail += str(data)
        last_cond = cond
    return detail


def get_outer_detail(data_list: [str], sep: str = " - "):
    """
        For remove repeat
    """
    detail = ""
    last_cond = False
    for data in data_list:
        cond = data != ""
        if cond and last_cond:
            detail += sep
        detail += str(data)
        last_cond = cond
    if detail != "":
        return "[ " + detail + " ] "
    else:
        return detail


class BaseLogHandler(logging.Handler):
    """
        A handler class which send data to anywhere
    """
    EXTRA_FIELDS = {"name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info",
                    "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread",
                    "threadName", "processName", "process", "message",
                    "logger_data", "extra_data", "short_message", "app_name", "host_name"}
    LOGGER_DATA = {"name", "levelname", "levelno", "pathname", "filename", "module",
                   "lineno", "funcName", "created", "msecs", "relativeCreated", "thread",
                   "threadName", "processName", "process"}

    def __init__(self, app_name: str = None, host_name: str = None, extra_data: dict = None):
        super().__init__()
        self.app_name = app_name
        self.host_name = host_name
        self.extra_data = extra_data

    def __get_logger_data(self, record: "logging.LogRecord"):
        """
            Get some log data
        """
        return {key: getattr(record, key, None) for key in self.LOGGER_DATA}

    def _get_send_data(self, record: logging.LogRecord):
        send_data = {
            "logger_data": self.__get_logger_data(record=record),
            "short_message": record.getMessage(),
        }
        if self.app_name is not None:
            send_data["app_name"] = self.app_name
        if self.host_name is not None:
            send_data["host_name"] = self.host_name
        if self.extra_data is not None:
            send_data["extra_data"] = self.extra_data

        for key, value in record.__dict__.items():
            if key not in self.EXTRA_FIELDS:
                if type(value) not in (bool, int, list, dict, str, float):
                    value = str(value)
                send_data[key] = value
        return send_data
