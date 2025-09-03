# DB values:
DEFAULT_CITY = 'Москва, Центральный федеральный фкруг, Россия'
DEFAULT_TZ = 'Europe/Moscow'
INT_USER_FIELDS = ('id', 'age', 'rating', 'points')
MAX_CITY_LEN = 256
MAX_NAME_LEN = 50
MAX_PHONE_NUMBER_LEN = 19
MAX_USERNAME_LEN = 32
SAFE_USER_FIELDS = ('name', 'age', 'city', 'phonenumber', 'interests', 'books',
                    'films', 'games', 'music')
EDITABLE_USER_FIELDS = SAFE_USER_FIELDS + ('username', 'role', 'timezone',
                                           'remindtime', 'rating', 'points')

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
