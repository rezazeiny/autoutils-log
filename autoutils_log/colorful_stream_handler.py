import logging
from typing import Dict, Tuple

import pytz
from termcolor import colored, cprint
# noinspection PyProtectedMember
from termcolor._types import Color

from .base import NOTSET, CRITICAL, ERROR, WARNING, INFO, DEBUG, get_inner_detail, get_outer_detail


class ColorfulStreamHandler(logging.StreamHandler):
    """
        A handler class which write stram handler.
    """
    LEVEL_COLOR_DATA: Dict[int, Tuple[str, Color]] = {
        NOTSET: ("NOTSET   ", "cyan"),
        CRITICAL: ("CRITICAL ", "light_red"),
        ERROR: ("ERROR    ", "red"),
        WARNING: ("WARNING  ", "blue"),
        INFO: ("INFO     ", "light_cyan"),
        DEBUG: ("DEBUG    ", "light_magenta"),
    }

    def __init__(self, colorful: bool = True, show_level: bool = True,
                 show_datetime: bool = True, datetime_color: Color = "green",

                 show_logger_name: bool = True, file_depth: int = 1, show_file: bool = True,
                 show_line: bool = True, show_func: bool = True, file_color: Color = "magenta",

                 show_process_name: bool = False, show_process_id: bool = False,
                 show_thread_name: bool = False, show_thread_id: bool = False,
                 process_thread_color: Color = "blue",

                 is_jalali: bool = True, timezone: str = None, datetime_format: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__()
        self.colorful = colorful
        self.show_level = show_level

        self.show_datetime = show_datetime
        self.datetime_color = datetime_color

        self.show_logger_name = show_logger_name
        self.file_depth = file_depth
        self.show_file = show_file
        self.show_line = show_line
        self.show_func = show_func
        self.file_color = file_color

        self.show_process_name = show_process_name
        self.show_process_id = show_process_id
        self.show_thread_name = show_thread_name
        self.show_thread_id = show_thread_id
        self.process_thread_color = process_thread_color

        self.is_jalali = is_jalali
        self.timezone = timezone
        self.datetime_format = datetime_format

    def get_color_text(self, text, color: Color):
        """
            Get Color Text
        """
        if self.colorful:
            return colored(text, color=color, force_color=True)
        else:
            return str(text)

    def get_datetime(self):
        """
            Get Time
        """
        if self.is_jalali:
            try:
                # noinspection PyPep8Naming
                from persiantools.jdatetime import JalaliDateTime as datetime
            except ImportError:
                cprint("Install persiantools library with pip install", color="red", force_color=True)
                from datetime import datetime
        else:
            from datetime import datetime
        tz = None
        if self.timezone:
            tz = pytz.timezone(self.timezone)
        return get_inner_detail([
            (self.show_datetime, datetime.now(tz=tz).strftime(self.datetime_format))
        ])

    def get_process_thread(self, record):
        """
            Process and thread detail
        """
        process_detail = get_inner_detail([
            (self.show_process_name, record.processName),
            (self.show_process_id, record.process)
        ])
        thread_detail = get_inner_detail([
            (self.show_thread_name, record.threadName),
            (self.show_thread_id, record.thread)
        ])
        return get_outer_detail([process_detail, thread_detail])

    def get_file_detail(self, record: logging.LogRecord):
        """
            Get File and line detail
        """
        logger_name = get_inner_detail([
            (self.show_logger_name, record.name),
        ])
        file_detail = get_inner_detail([
            (self.show_file, "/".join(record.pathname.split("/")[-self.file_depth:])),
            (self.show_line, record.lineno),
        ])
        function_detail = get_inner_detail([
            (self.show_func, record.module + "()"),
        ])

        return get_outer_detail([logger_name, file_detail, function_detail])

    def get_level(self, record):
        """
            Get Level
        """
        return get_inner_detail([
            (self.show_level, self.LEVEL_COLOR_DATA.get(record.levelno, ("",))[0])
        ])

    def get_level_color(self, record) -> Color:
        """
            Get Level Color
        """
        default: Tuple[str, Color] = ("", "yellow")
        color_data: Tuple[str, Color] = self.LEVEL_COLOR_DATA.get(record.levelno, default)
        return color_data[1]

    def format(self, record):
        """
        Format the specified record.

        If a formatter is set, use it. Otherwise, use the default formatter
        for the module.
        """
        # noinspection PyUnresolvedReferences,PyProtectedMember
        formatter = logging._defaultFormatter
        record.message = record.getMessage()

        color = self.get_level_color(record)

        color_datetime = self.get_color_text(self.get_datetime(), color=self.datetime_color)
        color_level = self.get_color_text(self.get_level(record), color=color)
        color_process_thread = self.get_color_text(self.get_process_thread(record),
                                                   color=self.process_thread_color)
        color_file_detail = self.get_color_text(self.get_file_detail(record), color=self.file_color)
        color_text = self.get_color_text(record.getMessage(), color=color)

        message = f"{color_datetime} {color_level}{color_process_thread}{color_file_detail}{color_text}"

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = formatter.formatException(record.exc_info)
        if record.exc_text:
            if message[-1:] != "\n":
                message += "\n"
            message += record.exc_text
        if record.stack_info:
            if message[-1:] != "\n":
                message += "\n"
            message += formatter.formatStack(record.stack_info)
        return message
