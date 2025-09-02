from telebot import TeleBot

from bot.handlers import (answer_to_invalid_msg, approve, check_profile,
                          check_students, handle_start_message)
from bot.settings import DEBUG
from core.loggers import get_logger
from scripts.env_config import DEBUG_TOKEN, WORKER_TOKEN


logger = get_logger(__name__)


bot = TeleBot(token=DEBUG_TOKEN if DEBUG
              else WORKER_TOKEN)  # type: ignore[arg-type]


def main():
    """The main bot logic."""
    bot.register_message_handler(approve, regexp=r'^\/approve_\d+$',
                                 pass_bot=True)
    bot.register_message_handler(check_profile, regexp=r'^\/profile(_\d+)?$',
                                 pass_bot=True)
    bot.register_message_handler(check_students, commands=['students'],
                                 pass_bot=True)
    bot.register_message_handler(handle_start_message, commands=['start'],
                                 pass_bot=True)
    bot.register_message_handler(answer_to_invalid_msg, pass_bot=True)

    logger.info('Handlers have been registered')
    bot.polling(interval=2)


if __name__ == '__main__':
    main()
