from telebot import TeleBot

from bot.handlers import (
    add_book, answer_to_invalid_msg, approve, check_books, check_interests,
    check_profile, check_students, delete_book, edit_profile, handle_help,
    handle_remind, handle_start_message, handle_user_field_update
)
from bot.settings import DEBUG
from core.constants import (
    ADD_BOOK, APPROVE, BOOKS, DELETE_BOOK, EDIT, HELP, INTERESTS, PROFILE,
    REMIND, START, STUDENTS, UPDATE
)
from core.loggers import get_logger
from scripts.env_config import DEBUG_TOKEN, WORKER_TOKEN


logger = get_logger(__name__)


bot = TeleBot(token=DEBUG_TOKEN if DEBUG
              else WORKER_TOKEN)  # type: ignore[arg-type]


def register_handlers(bot: TeleBot):
    """Registers all bot handlers."""
    bot.register_message_handler(add_book, commands=[ADD_BOOK], pass_bot=True)
    bot.register_message_handler(approve, regexp=fr'^\/{APPROVE}_\d+$',
                                 pass_bot=True)
    bot.register_message_handler(check_books, commands=[BOOKS], pass_bot=True)
    bot.register_message_handler(check_interests, pass_bot=True,
                                 regexp=fr'^\/{INTERESTS}(_\d+)?$')
    bot.register_message_handler(
        check_profile,
        regexp=fr'^(\/{PROFILE}(_\d+)?)$|^\U0001F464Профиль$',
        pass_bot=True
    )
    bot.register_message_handler(check_students, commands=[STUDENTS],
                                 pass_bot=True)
    bot.register_message_handler(delete_book, commands=[DELETE_BOOK],
                                 pass_bot=True)
    bot.register_message_handler(edit_profile, regexp=fr'^\/{EDIT}_\d+$',
                                 pass_bot=True)
    bot.register_message_handler(handle_help, pass_bot=True,
                                 regexp=fr'^\/{HELP}$|^\U00002754Помощь$')
    bot.register_message_handler(handle_remind, commands=[REMIND],
                                 pass_bot=True)
    bot.register_message_handler(handle_start_message, commands=[START],
                                 pass_bot=True)
    bot.register_message_handler(handle_user_field_update, pass_bot=True,
                                 regexp=fr'^\/{UPDATE}_\d+_[a-z]+$')
    bot.register_message_handler(answer_to_invalid_msg, pass_bot=True)

    logger.info('Handlers have been registered')


def main():
    """The main bot logic."""
    register_handlers(bot)

    bot.polling(interval=2)


if __name__ == '__main__':
    main()
