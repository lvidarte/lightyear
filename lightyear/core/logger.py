"""Logger
"""

import sys
import logging

from . import config

log_level = logging.DEBUG


def set_level(level):
    global log_level
    log_level = {
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }[level]


def get_logger(name='main-0', level=None):
    global log_level
    if level is None:
        levle = log_level
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    fmt = "[ %(levelname)s ] %(asctime)s | %(name)s (pid %(process)d) | %(message)s"
    formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
