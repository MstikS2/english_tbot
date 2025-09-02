from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message

from bot.permissions import has_debug_permission, is_staff_id
from core.exceptions import ToUserError
from core.constants import ADMIN, DEV, PENDING, STRANGER, STUDENT
from core.loggers import get_logger
from db.crud import create_obj, get_by_id, get_obj_list_where, update_obj
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
    logger.info(f'Message recieved:{message.text} by {user_id}')
    if not has_debug_permission(user_id):
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
    logger.info(f'Message recieved:{name} by {user_id}')
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
    logger.info(f'Message recieved:{city} by {user_id}')
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
    logger.info(f'Message recieved:{command} by {user_id}')
    if command == '/deny':
        logger.info('City have been geocoded wrong')
        send_text_message(bot, user_id, 'Введите город с дополнительной '
                          'информацией о нём')
        bot.register_next_step_handler(message, get_city, bot, user)
    elif command == '/confirm':
        logger.info('City have been geocoded right')
        user.city = geocoded_city
        user.timezone = tz
        finish_registration(message, bot, user)
    else:
        answer_to_invalid_msg(message, bot)
        bot.register_next_step_handler(message, confirm_city, bot, user)


def finish_registration(message, bot, user):
    """Sends approval request to admin."""
    if not is_staff_id(user.id):
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
        if not is_staff_id(user.id):
            username = user.username
            confirmation_msg = ('Новый пользователь регистрируется '
                                f'в боте: {user.name}')
            if username:
                confirmation_msg += f' @{username}'
            send_text_message(
                bot,
                ADMIN_ID,
                confirmation_msg + f'. Принять ученика: /approve_{user.id}'
            )
        else:
            send_text_message(bot, user.id, 'Вы и есть администратор... '
                                            'Одобрено!')
    logger.info(f'{user.id} successfully registered')


def approve(message: Message, bot: TeleBot):
    """Approves user registration."""
    user_id = message.chat.id
    logger.info(f'Message recieved:{message.text} by {user_id}')
    if not is_staff_id(user_id):
        return answer_to_invalid_msg(message, bot)
    new_user_id = int(message.text.split('_')[1])  # type: ignore[union-attr]
    new_user = get_by_id(User, new_user_id)
    if new_user.role != PENDING:
        return send_text_message(bot, user_id, 'Этот пользователь уже одобрен')
    new_user.role = STUDENT
    try:
        update_obj(new_user)
    except ToUserError as err:
        send_text_message(bot, user_id, str(err))
    else:
        logger.info('New student have been approved: '
                    f'{new_user.name} {new_user_id}')
        send_text_message(
            bot,
            user_id,
            'Пользователь принят в падаваны!\n'
            f'Его профиль: /profile_{new_user_id}'
        )
        send_text_message(
            bot,
            new_user_id,
            'Проверка администратором успешно пройдена! '
            'Весь функционал бота доступен'
        )


def check_profile(message: Message, bot: TeleBot):
    """Shows the information about user."""
    user_id = message.chat.id
    command = message.text
    logger.info(f'Message recieved:{command} by {user_id}')
    items = command.split('_')  # type: ignore[union-attr]
    if len(items) > 1:
        inspected_id = int(items[1])
        interests_command = f'interests_{inspected_id}'
        if inspected_id != user_id and not is_staff_id(user_id):
            return answer_to_invalid_msg(message, bot)
    else:
        inspected_id = user_id
        interests_command = 'interests'
    inspected_user = get_by_id(User, inspected_id)
    if not inspected_user:
        logger.error(f'User {user_id} inspected non-existent user '
                     f'{inspected_user}')
        return send_text_message(
            bot,
            user_id,
            'Что-то пошло не так! '
            'Пожалуйста, сообщите администратору или попробуйте позже'
        )
    profile_msg = (
        '\U0001F464 Профиль пользователя:\n\n'
        f'\U00000023\U000020E3 ID: {inspected_id}\n'
        f'\U0001F64E Имя: {inspected_user.name}\n'
        '\U000023F3 Возраст: '
        f'{inspected_user.age if inspected_user.age else 'не указано'}\n'
        f'\U0001F306 Город: {inspected_user.city}\n'
        '\U0001F4F1 Номер телефона: '
        '{}\n\n'.format(inspected_user.phone_number
                        if inspected_user.phone_number else 'не указано') +
        f'\U0001FA99 Баллы: {inspected_user.points}\n'
    )
    if is_staff_id(user_id):
        profile_msg += (
            '\n\U00002139 Информация ниже видна только вам, как админу:\n'
            '@ Юзернейм: '
            '@{}\n'.format(inspected_user.username
                           if inspected_user.username else 'отсутствует') +
            f'\U0001F46E Роль: {inspected_user.role}\n'
            f'\U0001F30D Часовой пояс: {inspected_user.timezone}\n'
            '\U0001F55C Установленное пользователем время напоминаний '
            f'о занятиях: {inspected_user.remind_time}\n'
            f'\U0001F3C5 Успеваемость: {inspected_user.rating}\n'
            f'\U0001F3EB Назначенные занятия:\n'
        )
        user_lessons = inspected_user.lessons
        if user_lessons:
            for lesson in user_lessons:
                profile_msg += f'{lesson.lesson_datetime}\n'
        else:
            profile_msg += 'Не назначено ни одного занятия\n'
    profile_msg += (
        f'\nИнтересы: /{interests_command}\n'
        f'Редактировать профиль: /edit_{inspected_id}'
    )
    send_text_message(bot, user_id, profile_msg)


def check_students(message: Message, bot: TeleBot):
    """Shows the list of all students."""
    user_id = message.chat.id
    logger.info(f'Message recieved:{message.text} by {user_id}')
    if not is_staff_id(user_id):
        return answer_to_invalid_msg(message, bot)
    students = get_obj_list_where(User, User.role == STUDENT)
    if not students:
        return send_text_message(bot, user_id, 'У вас пока нет учеников '
                                               '\U0001F615')
    list_message = 'Вот список учеников:\n\n'
    for number, student in enumerate(students):
        list_message += f'{number + 1}) {student.name} /profile_{student.id}\n'
    send_text_message(bot, user_id, list_message)


def answer_to_invalid_msg(message: Message, bot: TeleBot):
    """If user message does not fit any handlers, this will appear."""
    logger.info(f'Unknown command recieved: {message.text}')
    send_text_message(bot, message.chat.id,
                      'Я не понимаю что Вы хотите :(')
