from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message

from core.loggers import get_logger


logger = get_logger(__name__)


def send_text_message(bot: TeleBot, chat_id: int, message: str):
    """Sends a text message to Telegram-chat."""
    try:
        bot.send_message(chat_id=chat_id, text=message)
        logger.info(f'Успешно отправлено сообщение: "{message}"')
    except ApiException:
        logger.error(f'Не уалось отправить сообщение: "{message}"')


def answer_to_invalid_msg(recieved_message: Message, bot: TeleBot):
    """If user message does not fit any handlers, this will appear."""
    logger.info(f'Unknown command recieved: {recieved_message.text}')
    send_text_message(bot, recieved_message.chat.id,
                      'Я не понимаю что ты хочешь')
