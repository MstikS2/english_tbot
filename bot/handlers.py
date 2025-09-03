from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message

from bot.permissions import (
    has_debug_permission, has_field_changing_permission, is_staff_id,
    is_user_or_staff
)
from core.exceptions import ToUserError
from core.constants import ADMIN, DEV, PENDING, STRANGER, STUDENT
from core.loggers import get_logger
from db.crud import (create_obj, get_by_id, get_obj_list_where, object_exists,
                     update_obj)
from db.models import User
from scripts.env_config import ADMIN_ID, NOMINATIM_USER_AGENT
from scripts.timezones import get_timezone_by_city
from scripts.views import field_or_unknown


logger = get_logger(__name__)


def get_user_id(message: Message):
    """Extracts user id from Message object and logs it."""
    user_id = message.chat.id
    logger.info(f'Message recieved:{message.text} by {user_id}')
    return user_id


def extract_user(asker_id, command, message: Message, bot: TeleBot):
    """Extracts user object from /command_id-like command."""
    items = command.split('_')  # type: ignore[union-attr]
    if len(items) > 1:
        inspected_id = int(items[1])
        if not is_user_or_staff(inspected_id, asker_id):
            return answer_to_invalid_msg(message, bot)
        command_postscript = f'_{inspected_id}'
    else:
        inspected_id = asker_id
        command_postscript = ''
    inspected_user = get_by_id(User, inspected_id)
    if not inspected_user:
        logger.error(f'User {asker_id} inspected non-existent user '
                     f'{inspected_user}')
        send_text_message(
            bot,
            asker_id,
            'Что-то пошло не так! Кажется, такого пользователя не существует. '
            'Если вы уверены, что всё делали правильно, пожалуйста, сообщите '
            'администратору или попробуйте позже'
        )
        raise ValueError
    return inspected_user, command_postscript


def send_text_message(bot: TeleBot, chat_id, message: str):
    """Sends a text message to Telegram-chat."""
    try:
        bot.send_message(chat_id=chat_id, text=message)
        logger.info(f'Успешно отправлено сообщение: "{message}"'
                    f'в чат {chat_id}')
    except ApiException:
        logger.error(f'Не уалось отправить сообщение: "{message}"')


# Registration section (step by step):
def handle_start_message(message: Message, bot: TeleBot):
    """
    Handles /start and:
    1) Sends message for already registered users;
    2) Creates User object for new users;
    3) Register ask_name handler.
    """
    user_id = get_user_id(message)
    if not has_debug_permission(user_id):
        return send_text_message(bot, user_id, 'You are not allowed to '
                                               'testing. Go away!')
    user = get_by_id(User, user_id)
    if user and user.role != STRANGER:
        return send_text_message(bot, user_id, 'Вы уже прошли регистрацию!')
    elif not user:
        logger.info(f'New user started the bot: {user_id}')
        try:
            create_obj(User(id=user_id, username=message.chat.username))
        except ToUserError as err:
            return send_text_message(bot, user_id, str(err))
    send_text_message(bot, user_id, 'Добро пожаловать! Давайте знакомиться. '
                                    'Введите Ваше имя:')
    bot.register_next_step_handler(message, get_name, bot)


def get_name(message: Message, bot: TeleBot):
    """Gets user's name, updates users's db object and asks for user's city."""
    user_id = get_user_id(message)
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
    user_id = get_user_id(message)
    city = message.text
    if city == '/skip' and user.role == STRANGER:
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
    user_id = get_user_id(message)
    command = message.text
    if command == '/deny':
        logger.info('City have been geocoded wrong')
        send_text_message(bot, user_id, 'Введите город с дополнительной '
                          'информацией о нём')
        bot.register_next_step_handler(message, get_city, bot, user)
    elif command == '/confirm':
        logger.info('City have been geocoded right')
        user.city = geocoded_city
        user.timezone = tz
        if user.role == STRANGER:
            finish_registration(message, bot, user)
        else:
            try:
                update_obj(user)
            except ToUserError as err:
                send_text_message(bot, user.id, str(err))
                bot.register_next_step_handler(message, confirm_city, bot,
                                               user)
            else:
                send_text_message(bot, user.id, 'Город упешно изменён!')
                logger.info(f'{user.id} successfully changed his city to'
                            f'{geocoded_city}')

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
    user_id = get_user_id(message)
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
# End of registration section


def check_interests(message: Message, bot: TeleBot):
    """Shows the information about user interests."""
    user_id = get_user_id(message)
    try:
        inspected_user, command_postscript = extract_user(
            user_id, message.text, message, bot
        )
    except ValueError:
        return None
    interests_msg = (
        '\U0001F3AD Интересы: '
        f'{field_or_unknown(inspected_user.interests)}\n\n'
        '\U0001F4D7 Любимые книги: '
        f'{field_or_unknown(inspected_user.books)}\n\n'
        '\U0001F3AC Любимые фильмы: '
        f'{field_or_unknown(inspected_user.films)}\n\n'
        '\U0001F3AF Любимые игры: '
        f'{field_or_unknown(inspected_user.games)}\n\n'
        '\U0001F3B6 Любимая музыка: '
        f'{field_or_unknown(inspected_user.music)}\n\n'
        f'Редактировать: /edit_{inspected_user.id}'
    )
    send_text_message(bot, user_id, interests_msg)


def check_profile(message: Message, bot: TeleBot):
    """Shows the information about user."""
    user_id = get_user_id(message)
    try:
        inspected_user, command_postscript = extract_user(
            user_id, message.text, message, bot
        )
    except ValueError:
        return None
    profile_msg = (
        '\U0001F464 Профиль пользователя:\n\n'
        f'\U00000023\U000020E3 ID: {inspected_user.id}\n'
        f'\U0001F64E Имя: {inspected_user.name}\n'
        f'\U000023F3 Возраст: {field_or_unknown(inspected_user.age)}\n'
        f'\U0001F306 Город: {inspected_user.city}\n'
        '\U0001F4F1 Номер телефона: '
        f'{field_or_unknown(inspected_user.phonenumber)}\n\n'
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
            f'о занятиях: {inspected_user.remindtime}\n'
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
        f'\nИнтересы: /interests{command_postscript}\n'
        f'Редактировать профиль: /edit_{inspected_user.id}'
    )
    send_text_message(bot, user_id, profile_msg)


def check_students(message: Message, bot: TeleBot):
    """Shows the list of all students."""
    user_id = get_user_id(message)
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


def edit_profile(message: Message, bot: TeleBot):
    """Shows commands to edit the profile."""
    user_id = get_user_id(message)
    inspected_id = int(message.text.split('_')[1])  # type: ignore[union-attr]
    if not (is_user_or_staff(inspected_id, user_id) and
            object_exists(User, inspected_id)):
        return answer_to_invalid_msg(message, bot)
    command_root = f'/update_{inspected_id}_'
    edit_message = (
        f'Изменить имя: {command_root}name\n'
        f'Изменить возраст: {command_root}age\n'
        f'Изменить город: {command_root}city\n'
        f'Изменить номер телефона: {command_root}phonenumber\n\n'
        f'Изменить интересы: {command_root}interests\n'
        f'Изменить любимые книги: {command_root}books\n'
        f'Изменить любимые фильмы: {command_root}films\n'
        f'Изменить любимые игры: {command_root}games\n'
        f'Изменить любимую музыку: {command_root}music'
    )
    if is_staff_id(user_id):
        edit_message += (
            '\n\n\U0000203C\U0000203C\U0000203C Опасная зона! Эти поля может '
            'изменять только админ (вы). Пользуйтесь этим только если точно '
            'знаете, что делаете \U0000203C\U0000203C\U0000203C\n\n'
            f'Изменить юзернейм(@): {command_root}username\n'
            f'Изменить роль: {command_root}role\n'
            f'Изменить часовой пояс: {command_root}timezone\n'
            f'Изменить время напоминания: {command_root}remindtime\n'
            f'Изменить успеваемость: {command_root}rating\n'
            f'Изменить баллы: {command_root}points'
        )
    send_text_message(bot, user_id, edit_message)


def handle_user_field_update(message: Message, bot: TeleBot):
    """Handles update command for fields and registers handler for getting new
    field value."""
    user_id = get_user_id(message)
    items = message.text.split('_')  # type: ignore[union-attr]
    inspected_id = items[1]
    field = items[2]
    if not has_field_changing_permission(inspected_id, user_id, field):
        return answer_to_invalid_msg(message, bot)
    user = get_by_id(User, inspected_id)
    if not user:
        return send_text_message(
            bot,
            user_id,
            'Что-то пошло не так! Кажется, такого пользователя не существует. '
            'Если вы уверены, что всё делали правильно, пожалуйста, сообщите '
            'администратору или попробуйте позже'
        )
    if field == 'city':
        send_text_message(bot, user_id, 'Введите город, по часовому поясу '
                                        'которого будут приходить уведомления')
        bot.register_next_step_handler(message, get_city, bot, user)
    else:
        send_text_message(bot, user_id, 'Введите обновлённые данные. '
                                        'Введите /cancel, если передумали')
        bot.register_next_step_handler(message, update_user_field, bot, field,
                                       user)


def update_user_field(message: Message, bot: TeleBot, field, user):
    """Gets field value and updates db object."""
    user_id = get_user_id(message)
    new_value = message.text
    if new_value == '/cancel':
        return send_text_message(bot, user_id, 'Отменено')
    # Saving old name in case user updating it so report about update for admin
    # is possible:
    old_name = user.name

    try:
        setattr(user, field, new_value)
        update_obj(user)
    except ToUserError as err:
        send_text_message(bot, user_id, str(err))
        logger.error(f'Error while updating {field} of {user.id} by {user_id}')
        bot.register_next_step_handler(message, update_user_field, bot, field,
                                       user)
    else:
        send_text_message(bot, user_id, 'Поле успешно обновлено! /profile')
        logger.info(f'User {user_id} succcessfully updated '
                    f'{field} of {user.id}')
        if not is_staff_id(user_id):
            send_text_message(
                bot,
                ADMIN_ID,
                f'Пользователь {old_name} обновил поле {field} следующей '
                f'информацией:\n\n{new_value}'
            )


def answer_to_invalid_msg(message: Message, bot: TeleBot):
    """If user message does not fit any handlers, this will appear."""
    logger.info(f'Unknown command recieved: {message.text}')
    send_text_message(
        bot,
        message.chat.id,
        'Я не понимаю, что Вы хотите :(\n'
        'Возможно, какие-то из указанных данных не верны. А возможно, я просто'
        ' пока не умею делать этого'
    )
