from django.db import models


class OpeningHoursWeekdays(models.TextChoices):
    MONDAY = "monday", "Monday"
    TUESDAY = "tuesday", "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY = "thursday", "Thursday"
    FRIDAY = "friday", "Friday"
    SATURDAY = "saturday", "Saturday"
    SUNDAY = "sunday", "Sunday"


class SiteMessageType(models.TextChoices):
    DANGER = "danger", "Danger/error"
    WARNING = "warning", "Warning"
    INFO = "info", "Info"
    SUCCESS = "success", "Success"
