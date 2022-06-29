from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.utils.timezone import is_naive, make_aware, utc


def make_utc(dt: datetime) -> datetime:
    """
    Make naive timezone aware utc.
    """
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)
    return dt


def aware_utcnow() -> datetime:
    """
    Make timezone aware utcnow.
    """
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt: datetime) -> int:
    """
    Convert time to epoch.
    """
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts: int) -> datetime:
    """
    Convert from epoch to utc.
    """
    return make_utc(datetime.utcfromtimestamp(ts))
