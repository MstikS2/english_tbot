from telebot import TeleBot

from bot.handlers import (
    answer_to_invalid_msg, approve, check_interests, check_profile,
    check_students, edit_profile, handle_help, handle_start_message,
    handle_user_field_update
)
from bot.settings import DEBUG
from core.loggers import get_logger
from scripts.env_config import DEBUG_TOKEN, WORKER_TOKEN


logger = get_logger(__name__)


bot = TeleBot(token=DEBUG_TOKEN if DEBUG
              else WORKER_TOKEN)  # type: ignore[arg-type]


def register_handlers(bot: TeleBot):
    """Registers all bot handlers."""
    bot.register_message_handler(approve, regexp=r'^\/approve_\d+$',
                                 pass_bot=True)
    bot.register_message_handler(check_interests,
                                 regexp=r'^\/interests(_\d+)?$', pass_bot=True)
    bot.register_message_handler(
        check_profile,
        regexp=r'^(\/profile(_\d+)?)$|^\U0001F464Профиль$',
        pass_bot=True
    )
    bot.register_message_handler(check_students, commands=['students'],
                                 pass_bot=True)
    bot.register_message_handler(edit_profile, regexp=r'^\/edit_\d+$',
                                 pass_bot=True)
    bot.register_message_handler(handle_help, pass_bot=True,
                                 regexp=r'^\/help$|^\U00002754Помощь$')
    bot.register_message_handler(handle_start_message, commands=['start'],
                                 pass_bot=True)
    bot.register_message_handler(handle_user_field_update, pass_bot=True,
                                 regexp=r'^\/update_\d+_[a-z]+$')
    bot.register_message_handler(answer_to_invalid_msg, pass_bot=True)

    logger.info('Handlers have been registered')


def main():
    """The main bot logic."""
    register_handlers(bot)

    bot.polling(interval=2)


if __name__ == '__main__':
    main()
