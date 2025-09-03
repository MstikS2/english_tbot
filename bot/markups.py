from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def profile_markup():
    """Creates a markup with profile button."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    profile_button = KeyboardButton('\U0001F464Профиль')
    markup.add(profile_button)
    return markup
