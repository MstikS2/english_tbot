from telebot import TeleBot

from bot.handlers import answer_invalid_msg
from bot.settings import DEBUG
from scripts.env_config import Env

env = Env()

bot = TeleBot(token=env.debug_token if DEBUG else env.worker_token)

bot.register_message_handler(answer_invalid_msg, pass_bot=True)

bot.polling(interval=2)
