from calendar import timegm
from datetime import datetime
from django.conf import settings
from django.utils.timezone import is_naive, utc, make_aware


def make_utc(dt: datetime) -> datetime:
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)
    return dt


def aware_utcnow() -> datetime:
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt: datetime) -> int:
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts: int) -> datetime:
    return make_utc(datetime.utcfromtimestamp(ts))
