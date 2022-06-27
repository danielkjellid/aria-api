from django.db import models


class OpeningHoursWeekdays(models.TextChoices):
    MONDAY = "monday", "Mandag"
    TUESDAY = "tuesday", "Tirsdag"
    WEDNESDAY = "wednesday", "Onsdag"
    THURSDAY = "thursday", "Torsdag"
    FRIDAY = "friday", "Fredag"
    SATURDAY = "saturday", "Lørdag"
    SUNDAY = "sunday", "Søndag"


class SiteMessageType(models.TextChoices):
    DANGER = "danger", "Danger/error"
    WARNING = "warning", "Warning"
    INFO = "info", "Info"
    SUCCESS = "success", "Success"
