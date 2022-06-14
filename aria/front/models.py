from typing import Iterable, Optional

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models

from aria.core.models import BaseModel
from aria.front.enums import OpeningHoursWeekdays, SiteMessageType
from aria.front.managers import (
    OpeningHoursDeviationQuerySet,
    OpeningHoursDeviationTemplateQuerySet,
    OpeningHoursQuerySet,
    OpeningHoursTimeSlotQuerySet,
    SiteMessageLocationQuerySet,
    SiteMessageQuerySet,
)

_OpeningHoursManager = models.Manager.from_queryset(OpeningHoursQuerySet)


class OpeningHours(models.Model):
    """
    Opening hours for a single site.
    """

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="opening_hours"
    )

    objects = _OpeningHoursManager()

    class Meta:
        verbose_name = "Opening hours"
        verbose_name_plural = "Opening hours"

    def __str__(self) -> str:
        return self.site.name

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Uncache opening hours on save.
        """

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        # Uncache all opening hours.
        cache.delete("opening_hours")


_OpeningHoursTimeSlotManager = models.Manager.from_queryset(
    OpeningHoursTimeSlotQuerySet
)


class OpeningHoursTimeSlot(models.Model):
    """
    A reusable time slot used when deciding opening hours.
    """

    opening_hours = models.ForeignKey(
        "front.OpeningHours",
        on_delete=models.SET_NULL,
        related_name="time_slots",
        null=True,
        blank=True,
    )
    weekday = models.CharField(choices=OpeningHoursWeekdays.choices, max_length=50)
    open_at = models.TimeField("Opening time", blank=True, null=True)
    close_at = models.TimeField("Closing time", blank=True, null=True)
    is_closed = models.BooleanField("Is closed on this day", default=False)

    objects = _OpeningHoursTimeSlotManager()

    class Meta:
        unique_together = (("opening_hours", "weekday"),)

    def __str__(self) -> str:
        return (
            f"{self.get_weekday_display()}: {self.open_at} - {self.close_at}"
            if not self.is_closed
            else f"{self.get_weekday_display()}: Closed"
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Uncache opening hours on save.
        """

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        # Uncache all opening hours messages.
        cache.delete("opening_hours")


_OpeningHoursDeviationManager = models.Manager.from_queryset(
    OpeningHoursDeviationQuerySet
)


class OpeningHoursDeviation(models.Model):
    """
    Deviation that affects normal opening hours, for example holidy.
    """

    opening_hours = models.ForeignKey(
        "front.OpeningHours", on_delete=models.CASCADE, related_name="deviations"
    )
    template = models.ForeignKey(
        "front.OpeningHoursDeviationTemplate",
        on_delete=models.SET_NULL,
        related_name="deviations",
        blank=True,
        null=True,
    )
    active_at = models.DateTimeField("Time when deviation is active from")
    active_to = models.DateTimeField("Time when deviation is active to")
    description = models.TextField(null=True, blank=False)

    disable_appointment_bookings = models.BooleanField(default=False)

    objects = _OpeningHoursDeviationManager()

    def __str__(self) -> str:
        return f"{self.opening_hours} deviation: {self.active_at - self.active_to}"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Uncache opening hours on save.
        """

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        # Uncache all opening hours messages.
        cache.delete("opening_hours")


_OpeningHoursDeviationTemplateManager = models.Manager.from_queryset(
    OpeningHoursDeviationTemplateQuerySet
)


class OpeningHoursDeviationTemplate(models.Model):
    """
    A predefined template for deviations. For example easter, christmas,
    etc.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=False)
    site_message = models.ForeignKey(
        "front.SiteMessage",
        on_delete=models.SET_NULL,
        related_name="deviation_templates",
        blank=True,
        null=True,
    )

    objects = _OpeningHoursDeviationTemplateManager()

    def __str__(self) -> str:
        return self.name


_SiteMessageLocationManager = models.Manager.from_queryset(SiteMessageLocationQuerySet)


class SiteMessageLocation(models.Model):
    """
    A location of where a site message is to be displayed. Can
    for example globally, front page, checkout, account page etc.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)

    objects = _SiteMessageLocationManager()

    def __str__(self) -> str:
        return self.name


_SiteMessageManager = models.Manager.from_queryset(SiteMessageQuerySet)


class SiteMessage(BaseModel):
    """
    A global warning, info or deviation message.
    """

    text = models.TextField(help_text="Message body, can contain some html.")
    message_type = models.CharField(max_length=50, choices=SiteMessageType.choices)
    locations = models.ManyToManyField(
        "front.SiteMessageLocation",
        blank=True,
        help_text="Locations to show this particular site message. Leave empty to display message at a global level.",
    )
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="site_messages"
    )
    show_message_at = models.DateTimeField(
        "Show from",
        null=True,
        blank=True,
        help_text="When the message should be visible from. Leave empty to display the message immediately.",
    )
    show_message_to = models.DateTimeField(
        "Show to",
        null=True,
        blank=True,
        help_text="When the message should disappear. Leave emtpy to display the message indefinitely",
    )

    objects = _SiteMessageManager()

    def __str__(self) -> str:
        return f"{self.get_message_type_display()} {self.show_message_at} - {self.show_message_to}"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Uncache site messages on save.
        """

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        # Uncache all site messages.
        cache.delete("site_messages")
