from os import getenv

from dotenv import load_dotenv

from core.loggers import get_logger


logger = get_logger(__name__)


def check_env():
    """Checks if all env values are specified."""
    empty_values = []
    for value in ENV_VALUES:
        if not value:
            empty_values.append(value)
    if empty_values:
        error_message = f'Values are not specified: {empty_values}'
        logger.critical(error_message)
        raise ValueError(error_message)


load_dotenv()
ADMIN_ID = getenv('ADMIN_ID')
DEV_ID = getenv('DEV_ID')
DEBUG_TOKEN = getenv('DEBUG_TOKEN')
NOMINATIM_USER_AGENT = getenv('NOMINATIM_USER_AGENT')
WORKER_TOKEN = getenv('WORKER_TOKEN')

ENV_VALUES = (ADMIN_ID, DEV_ID, DEBUG_TOKEN, NOMINATIM_USER_AGENT,
              WORKER_TOKEN)

check_env()
