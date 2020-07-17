import configparser
import datetime
import logging
import os

config = configparser.ConfigParser()
_read = config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
if not _read:
    raise configparser.Error('Config file not found')


def get_logger(name):
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_name = '{name}_{date}.log'.format(name=name, date=datetime.date.today())
    file_path = os.path.join('logs', file_name)

    log_file_handler = logging.FileHandler(file_path, 'a')
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger(name)
    logger.addHandler(log_file_handler)

    return logger
