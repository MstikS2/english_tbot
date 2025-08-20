from telebot import TeleBot

from bot.handlers import answer_to_invalid_msg, approve, handle_start_message
from bot.settings import DEBUG
from core.loggers import get_logger
from scripts.env_config import DEBUG_TOKEN, WORKER_TOKEN


logger = get_logger(__name__)


bot = TeleBot(token=DEBUG_TOKEN if DEBUG
              else WORKER_TOKEN)  # type: ignore[arg-type]

bot.register_message_handler(approve, regexp=r'^\/approve_\d+$', pass_bot=True)
bot.register_message_handler(handle_start_message, commands=['start'],
                             pass_bot=True)
bot.register_message_handler(answer_to_invalid_msg, pass_bot=True)

logger.info('Handlers have been registered')


def main():
    """The main bot logic."""
    bot.polling(interval=2)


if __name__ == '__main__':
    main()
