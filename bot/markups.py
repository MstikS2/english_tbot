from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def profile_markup():
    """Creates a markup with profile button."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = KeyboardButton('\U0001F464Профиль')
    help_button = KeyboardButton('\U00002754Помощь')
    markup.add(profile_button, help_button)
    return markup
