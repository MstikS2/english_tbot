from pytz import timezone

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from core.error_messages import INVALID_CITY_MSG


def get_city_location(city: str, nominatim_user_agent: str):
    """Gets cityname and returns its location."""
    geolocator = Nominatim(user_agent=nominatim_user_agent, timeout=10)
    loc = geolocator.geocode(city)
    if not loc:
        raise ValueError(INVALID_CITY_MSG)
    return loc


def get_timezone_by_city(city: str, nominatim_user_agent: str):
    """Gets cityname and returns timezone."""
    loc = get_city_location(city, nominatim_user_agent)
    tzfinder = TimezoneFinder()
    return timezone(tzfinder.timezone_at(lng=loc.longitude, lat=loc.latitude))
