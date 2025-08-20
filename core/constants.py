# DB values:
DEFAULT_CITY = 'Москва, Центральный федеральный фкруг, Россия'
DEFAULT_TZ = 'Europe/Moscow'
MAX_NAME_LEN = 50
MAX_PHONE_NUMBER_LEN = 19
MAX_USERNAME_LEN = 32

# User roles:
ADMIN, DEV, PENDING, STRANGER, STUDENT = ('admin', 'dev', 'pending',
                                          'stranger', 'student',)
STAFF = (ADMIN, DEV)
USER_ROLES = STAFF + (PENDING, STRANGER, STUDENT)

# Logging staff:
LOG_DIR = 'logs'
LOG_FORMATTER_MSG = ('%(asctime)s| %(levelname)s| %(name)s - %(funcName)s: '
                     '%(message)s')
LOG_MAXBYTES = 50000000
