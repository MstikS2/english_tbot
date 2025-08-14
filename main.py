from telebot import TeleBot

from bot.handlers import answer_to_invalid_msg
from bot.settings import DEBUG
from core.loggers import get_logger
from scripts.env_config import Env


logger = get_logger(__name__)


env = Env()

bot = TeleBot(token=env.debug_token if DEBUG else env.worker_token)

bot.register_message_handler(answer_to_invalid_msg, pass_bot=True)

logger.debug('Handlers have been registered')


def main():
    """The main bot logic."""
    bot.polling(interval=2)


if __name__ == '__main__':
    main()
