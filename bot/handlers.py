from telebot import TeleBot

from core.bot_messages import UNKNOWN_MSG


def answer_invalid_msg(message, bot: TeleBot):
    """If user message does not fit any handlers, this will appear."""
    bot.send_message(chat_id=message.chat.id, text=UNKNOWN_MSG)
