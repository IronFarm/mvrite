import logging
import os

import configparser

config = configparser.ConfigParser()
_read = config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
if not _read:
    raise configparser.Error('Config file not found')


def get_logger(name):
    return logging.getLogger(name)
