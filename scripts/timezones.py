from pytz import timezone

from geopy.geocoders import Nominatim
from geopy.exc import ConfigurationError, GeocoderTimedOut
from timezonefinder import TimezoneFinder

from core.exceptions import ToUserError
from core.loggers import get_logger


logger = get_logger(__name__)


def get_city_location(city: str, nominatim_user_agent: str):
    """Gets cityname and returns its location."""
    geolocator = Nominatim(user_agent=nominatim_user_agent, timeout=10)
    loc = geolocator.geocode(city)
    if not loc:
        raise ValueError('Не удалось найти город. '
                         'Проверьте название города и повторите попытку')
    return loc


def get_timezone_by_city(city: str, nominatim_user_agent: str):
    """Gets cityname and returns timezone."""
    try:
        loc = get_city_location(city, nominatim_user_agent)
    except ConfigurationError as err:
        logger.error(f'Failed to connect to Nominatim: {err}')
        raise ToUserError(
            'Сбой при подключении к сервису часовых поясов. '
            'Пожалуйста, свяжитесь с администратором и сообщите об ошибке'
        )
    except GeocoderTimedOut as err:
        logger.error(f'Failed to connect to Nominatim: {err}')
        raise ToUserError(
            'Сервис для определения часовых поясов временно недоступен. '
            'Пожалуйста, повторите попытку позднее'
        )
    except ValueError as err:
        logger.info(f'User probably entered an invalid city: {city}')
        raise ToUserError(err)
    tzfinder = TimezoneFinder()
    return timezone(tzfinder.timezone_at(lng=loc.longitude, lat=loc.latitude))
