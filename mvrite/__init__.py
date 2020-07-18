import configparser
import datetime
import logging
import os

config = configparser.ConfigParser()
_read = config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
if not _read:
    raise configparser.Error('Config file not found')


def get_logger(name):
    dir_name = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    file_name = '{name}_{date}.log'.format(name=name, date=datetime.date.today())
    file_path = os.path.join(dir_name, file_name)

    logger = logging.getLogger(name)

    # Add new handler if necessary
    if not logger.handlers:
        log_file_handler = logging.FileHandler(file_path, 'a')
        log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.addHandler(log_file_handler)

    return logger
