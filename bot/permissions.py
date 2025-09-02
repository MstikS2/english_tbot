from bot.settings import DEBUG
from scripts.env_config import ADMIN_ID, DEV_ID


def has_debug_permission(user_id) -> bool:
    """Returns False if DEBUG is True and user with given_id is not staff,
    else True."""
    return not (DEBUG and not is_staff_id(user_id))


def is_staff_id(user_id) -> bool:
    """Returns True if user with given id is staff, else False."""
    return str(user_id) in (ADMIN_ID, DEV_ID)


def is_user_or_staff(inspected_id, user_id) -> bool:
    """Returns True if user incpects himself or he is staff, else False."""
    return inspected_id == user_id or is_staff_id(user_id)
