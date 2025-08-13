import os
from pytz import timezone

from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from core.error_messages import INVALID_CITY_MSG

load_dotenv()


def get_city_location(city: str):
    """Gets cityname and returns its location."""
    geolocator = Nominatim(user_agent=os.getenv('NOMINATIM_USER_AGENT'),
                           timeout=10)
    loc = geolocator.geocode(city)
    if not loc:
        raise ValueError(INVALID_CITY_MSG)
    return loc


def get_timezone_by_city(city: str):
    """Gets cityname and returns timezone."""
    loc = get_city_location(city)
    tzfinder = TimezoneFinder()
    return timezone(tzfinder.timezone_at(lng=loc.longitude, lat=loc.latitude))
