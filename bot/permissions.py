from bot.settings import DEBUG
from scripts.env_config import ADMIN_ID, DEV_ID


def check_debug_permission(user_id):
    """Returns False if DEBUG is True and user with given_id is not staff,
    else True."""
    return not (DEBUG and not check_staff_id(user_id))


def check_staff_id(user_id):
    """Returns True if user with given id is staff, else False."""
    return str(user_id) in (ADMIN_ID, DEV_ID)
