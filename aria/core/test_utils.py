from datetime import timedelta
from django.conf import settings


def model_baker_datetime_formatting(datetime) -> str:
    """
    Models created by model_bakery is one hour behind tz.

    This causes problems when comparing outputs.
    """

    return (datetime + timedelta(hours=1)).strftime(settings.DATETIME_FORMAT)
