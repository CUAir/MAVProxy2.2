''' 
MAVProxy logger to be used by all modules
'''

import logging
import datetime
import os
from termcolor import colored

LOG_FILE_PATH = "../test_flight/autopilot_logs"

DEBUG_COLOR = 'grey'
INFO_COLOR = 'green'
WARNING_COLOR = 'yellow'
ERROR_COLOR = 'red'
CRITICAL_COLOR = 'red'

DEBUG_ATTRS = []
INFO_ATTRS = []
WARNING_ATTRS = []
ERROR_ATTRS = []
CRITICAL_ATTRS = ['bold']

class ColorFormatter(logging.Formatter):
    def format(self, record):
        prev_format = self._fmt
        if record.levelno == logging.DEBUG:
            self._fmt = colored('%(name)s', DEBUG_COLOR, attrs=DEBUG_ATTRS) + ': %(message)s'
        elif record.levelno == logging.INFO:
            self._fmt = colored('%(name)s', INFO_COLOR, attrs=INFO_ATTRS) + ': %(message)s'
        elif record.levelno == logging.WARNING:
            self._fmt = colored('%(name)s', WARNING_COLOR, attrs=WARNING_ATTRS) + ': %(message)s'
        elif record.levelno == logging.ERROR:
            self._fmt = colored('%(name)s', ERROR_COLOR, attrs=ERROR_ATTRS) + ': %(message)s'
        elif record.levelno == logging.CRITICAL:
            self._fmt = colored('%(name)s', CRITICAL_COLOR, attrs=CRITICAL_ATTRS) + ': %(message)s'
        else:
            self._fmt = self._fmt # For readability - if we don't recognize the log level, keep the old format

        result = logging.Formatter.format(self, record)
        self._fmt = prev_format
        return result


# Should be used as follows:
# import MAVProxy.mavproxy_logging
# logger = MAVProxy.mavproxy_logging.create_logger("Module Name")
# logger.[debug/info/warning/error/critical]("My log message")

# Name should be unique to the module it's coming from
def create_logger(name):
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = ColorFormatter('(%(levelname)s) %(name)s: %(message)s')
    
    log_name = datetime.date.today().strftime("%d-%m-%y")
    mavproxy_path = os.path.dirname(os.path.realpath(__file__))

    path = mavproxy_path + "/" + LOG_FILE_PATH

    fileHandler = logging.FileHandler("{0}/{1}.log".format(path, log_name))
    file_formatter = logging.Formatter('%(asctime)s | (%(levelname)s) %(name)s: %(message)s')
    fileHandler.setFormatter(file_formatter)
    logger.addHandler(fileHandler)

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

def get_log_path():
    mavproxy_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(mavproxy_path, LOG_FILE_PATH)
