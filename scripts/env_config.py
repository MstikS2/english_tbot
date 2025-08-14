from os import getenv

from dotenv import load_dotenv

from core.loggers import get_logger


logger = get_logger(__name__)


class Env:
    """Class for accessing env values."""

    def __init__(self):
        self.__load_env()
        self.__check_env()
        logger.info('.env loaded successfully')

    def __check_env(self):
        """Checks if all env values are specified."""
        empty_values = []
        for value in self.__values:
            if not value:
                empty_values.append(value)
        if empty_values:
            error_message = f'Values are not specified: {empty_values}'
            logger.critical(error_message)
            raise ValueError(error_message)

    def __load_env(self):
        """Loads and returns values from env."""
        load_dotenv()
        self.admin_id = getenv('ADMIN_ID')
        self.dev_id = getenv('DEV_ID')
        self.debug_token = getenv('DEBUG_TOKEN')
        self.nominatim_user_agent = getenv('NOMINATIM_USER_AGENT')
        self.worker_token = getenv('WORKER_TOKEN')
        self.__values = (self.admin_id, self.dev_id, self.debug_token,
                         self.nominatim_user_agent, self.worker_token)
