from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message

from bot.permissions import check_debug_permission, check_staff_id
from core.exceptions import ToUserError
from core.constants import ADMIN, DEV, PENDING, STRANGER
from core.loggers import get_logger
from db.crud import create_obj, get_by_id, update_obj
from db.models import User
from scripts.env_config import ADMIN_ID, NOMINATIM_USER_AGENT
from scripts.timezones import get_timezone_by_city


logger = get_logger(__name__)


def send_text_message(bot: TeleBot, chat_id, message: str):
    """Sends a text message to Telegram-chat."""
    try:
        bot.send_message(chat_id=chat_id, text=message)
        logger.info(f'Успешно отправлено сообщение: "{message}"'
                    f'в чат {chat_id}')
    except ApiException:
        logger.error(f'Не уалось отправить сообщение: "{message}"')


def handle_start_message(message: Message, bot: TeleBot):
    """
    Handles /start and:
    1) Sends message for already registered users;
    2) Creates User object for new users;
    3) Register ask_name handler.
    """
    chat = message.chat
    user_id = chat.id
    if not check_debug_permission(user_id):
        return send_text_message(bot, user_id, 'You are not allowed to '
                                               'testing. Go away!')
    user = get_by_id(User, user_id)
    if user and user.role != STRANGER:
        return send_text_message(bot, user_id, 'Вы уже прошли регистрацию!')
    elif not user:
        logger.info(f'New user started the bot: {user_id}')
        try:
            create_obj(User(id=user_id, username=chat.username))
        except ToUserError as err:
            return send_text_message(bot, user_id, str(err))
    send_text_message(bot, user_id, 'Добро пожаловать! Давайте знакомиться. '
                                    'Введите Ваше имя:')
    bot.register_next_step_handler(message, get_name, bot)


def get_name(message: Message, bot: TeleBot):
    """Gets user's name, updates users's db object and asks for user's city."""
    user_id = message.chat.id
    name = message.text
    # In case of the user accidentally pressed the /start command
    # multiple times:
    if name == '/start':
        return handle_start_message(message, bot)
    user = get_by_id(User, user_id)
    user.name = name
    try:
        update_obj(user)
    except ToUserError as err:
        send_text_message(bot, user_id, str(err))
        bot.register_next_step_handler(message, get_name, bot)
    else:
        send_text_message(
            bot,
            user_id,
            f'Приятно познакомиться, {name}!\n'
            '\n'
            'Чтобы информация о предстоящих занятиях была показана в Вашем '
            'часовом поясе, введите Ваш город. Либо /skip - тогда информация '
            'о занятиях будет отображаться в московском времени (GMT+3). '
            'Город можно будет изменить в любой момент'
        )
        bot.register_next_step_handler(message, get_city, bot, user)


def get_city(message: Message, bot: TeleBot, user):
    """Gets user's city, updates users's db object
    and asks for confirmation."""
    user_id = message.chat.id
    city = message.text
    if city == '/skip':
        return finish_registration(message, bot, user)
    send_text_message(bot, user_id, 'Запрос обрабатывается...')
    try:
        geocoded_city, tz = get_timezone_by_city(city, NOMINATIM_USER_AGENT)
        geocoded_city, tz = str(geocoded_city), str(tz)
        logger.info(f'City have been geocoded: {city} as {geocoded_city}')
    except ToUserError as err:
        send_text_message(bot, user_id, str(err))
        bot.register_next_step_handler(message, get_city, bot, user)
    else:
        send_text_message(
            bot,
            user_id,
            'Проверьте правильность полученного населённого пункта:\n'
            '\n'
            f'{geocoded_city}\n'
            '\n'
            'Если всё правильно, введите /confirm. Если присутствует ошибка, '
            'введите /deny, а затем попробуйте ввести более точную '
            'информацию, например, так:\n'
            '\n'
            'Город, Регион, Страна'
        )
        bot.register_next_step_handler(message, confirm_city, bot,
                                       geocoded_city, tz, user)


def confirm_city(message: Message, bot: TeleBot, geocoded_city, tz, user):
    """Update user's city and tz and sends him for admin approval
    if confirmed or asks for new one if denied."""
    user_id = message.chat.id
    command = message.text
    if command == '/deny':
        logger.info('City have been geocoded wrong')
        send_text_message(bot, user_id, 'Введите город с дополнительной '
                          'информацией о нём')
        bot.register_next_step_handler(message, get_city, bot, user)
    elif command == '/confirm':
        logger.info('City have been geocoded right')
        user.city = geocoded_city
        user.user_timezone = tz
        finish_registration(message, bot, user)
    else:
        answer_to_invalid_msg(message, bot)
        bot.register_next_step_handler(message, confirm_city, bot, user)


def finish_registration(message, bot, user):
    """Sends approval request to admin."""
    if not check_staff_id(user.id):
        user.role = PENDING
    elif str(user.id) == ADMIN_ID:
        user.role = ADMIN
    else:
        user.role = DEV
    try:
        update_obj(user)
    except ToUserError as err:
        send_text_message(bot, user.id, str(err))
        bot.register_next_step_handler(message, finish_registration, bot, user)
    else:
        send_text_message(
            bot,
            user.id,
            'Готово! Ожидайте проверки администратором. А пока, '
            'если хотите, можете настроить свой профиль: /profile'
        )
        if not check_staff_id(user.id) or user.role == DEV:
            username = user.username
            confirmation_msg = ('Новый пользователь регистрируется '
                                f'в боте: {user.name}')
            if username:
                confirmation_msg += f' @{username}'
            send_text_message(
                bot,
                ADMIN_ID,
                confirmation_msg + f'. Принять ученика: /confirm_{user.id}'
            )
        else:
            send_text_message(bot, user.id, 'Вы и есть администратор... '
                                            'Одобрено!')
    logger.info(f'{user.id} successfully registered')


def answer_to_invalid_msg(message: Message, bot: TeleBot):
    """If user message does not fit any handlers, this will appear."""
    logger.info(f'Unknown command recieved: {message.text}')
    send_text_message(bot, message.chat.id,
                      'Я не понимаю что Вы хотите :(')
