"""Logger
"""

import logging
import sys

log_level = logging.DEBUG
fmt = "[ %(levelname)s ] %(asctime)s | %(name)s (pid %(process)d) | %(message)s"


def set_level(level):
    global log_level
    # fmt: off
    log_level = {
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }[level]
    # fmt: on


def get_logger(name="main-0", level=None):
    global log_level
    if level is None:
        level = log_level
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
