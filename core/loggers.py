import logging
from logging.handlers import RotatingFileHandler

from core.constants import LOG_DIR, LOG_FORMATTER_MSG, LOG_MAXBYTES


def get_logger(name):
    """Gets module __name__ (or any other name) and returns Logger object."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        f'{LOG_DIR}/{name}.log',
        maxBytes=LOG_MAXBYTES,
        backupCount=2,
        encoding='utf-8'
    )
    formatter = logging.Formatter(LOG_FORMATTER_MSG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
