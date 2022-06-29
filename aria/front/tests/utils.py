from datetime import datetime, time

from django.contrib.sites.models import Site
from django.utils import timezone

from aria.core.tests.utils import create_site
from aria.front.enums import OpeningHoursWeekdays, SiteMessageType
from aria.front.models import (
    OpeningHours,
    OpeningHoursDeviation,
    OpeningHoursDeviationTemplate,
    OpeningHoursTimeSlot,
    SiteMessage,
    SiteMessageLocation,
)


def create_site_message_location(
    *,
    name: str = "Test location",
    description: str = "Test location for test purposes",
    slug: str | None = None,
) -> SiteMessageLocation:
    """
    Test utility to create a SiteMessageLocation instance.
    """

    if not slug:
        slug = "test-location"

    site_message_location, _created = SiteMessageLocation.objects.get_or_create(
        slug=slug, defaults={"name": name, "description": description}
    )

    return site_message_location


def create_site_message(
    *,
    text: str = "Test site message",
    message_type: SiteMessageType = SiteMessageType.INFO,
    locations: list[SiteMessageLocation] | None = None,
    site: Site | None = None,
    show_message_at: datetime,
    show_message_to: datetime,
) -> SiteMessage:
    """
    Test utility to create a SiteMessage instance.
    """

    if not site:
        site = create_site()

    if not locations:
        locations = [create_site_message_location()]

    site_message, _created = SiteMessage.objects.update_or_create(
        text=text,
        site=site,
        message_type=message_type,
        show_message_at=show_message_at,
        show_message_to=show_message_to,
    )

    site_message.locations.set(locations)

    return site_message


def create_opening_hours_time_slot(
    *,
    opening_hours_id: int | None = None,
    opening_hours_deviation_id: int | None = None,
    weekday: OpeningHoursWeekdays,
    opening_at: time | None,
    closing_at=time | None,
    is_closed: bool = False,
) -> OpeningHoursTimeSlot:
    """
    Test utility to create a OpeningHoursTimeSlot instance.
    """
    time_slot, _created = OpeningHoursTimeSlot.objects.get_or_create(
        opening_hours_id=opening_hours_id,
        opening_hours_deviation_id=opening_hours_deviation_id,
        weekday=weekday,
        opening_at=opening_at,
        closing_at=closing_at,
        is_closed=is_closed,
    )

    return time_slot


def create_opening_hours(
    *, site: Site | None = None, time_slots: list[OpeningHoursTimeSlot] | None = None
) -> OpeningHours:
    """
    Test utility to create an OpeningHours instance.
    """
    if site is None:
        site = create_site()

    opening_hours, _created = OpeningHours.objects.get_or_create(site=site)

    if not time_slots:
        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.MONDAY,
            opening_at="09:00:00",
            closing_at="17:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.TUESDAY,
            opening_at="09:00:00",
            closing_at="17:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.WEDNESDAY,
            opening_at="09:00:00",
            closing_at="17:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.THURSDAY,
            opening_at="09:00:00",
            closing_at="17:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.FRIDAY,
            opening_at="09:00:00",
            closing_at="16:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.SATURDAY,
            opening_at="10:00:00",
            closing_at="15:00:00",
            is_closed=False,
        )

        create_opening_hours_time_slot(
            opening_hours_id=opening_hours.id,
            weekday=OpeningHoursWeekdays.SUNDAY,
            opening_at=None,
            closing_at=None,
            is_closed=True,
        )

    return opening_hours


def create_opening_hours_deviation(
    *,
    opening_hours_id: int,
    active_at: datetime,
    active_to: datetime,
    description: str = "Opening hours deviation",
    disable_appointment_bookings: bool = False,
) -> OpeningHoursDeviation:
    """
    Test utility to create a OpeningHoursDeviation instance.
    """

    oh_deviation = OpeningHoursDeviation.objects.create(
        opening_hours_id=opening_hours_id,
        template=create_opening_hours_deviation_template(),
        active_at=active_at,
        active_to=active_to,
        description=description,
        disable_appointment_bookings=disable_appointment_bookings,
    )

    create_opening_hours_time_slot(
        opening_hours_deviation_id=oh_deviation.id,
        weekday=OpeningHoursWeekdays.WEDNESDAY,
        opening_at=None,
        closing_at=None,
        is_closed=True,
    )

    return oh_deviation


def create_opening_hours_deviation_template(
    *,
    name: str = "Deviation test template",
    description: str = "Testing template",
    site_message: SiteMessage | None = None,
) -> OpeningHoursDeviationTemplate:
    """
    Test utility to create a OpeningHoursDeviationTemplate instance.
    """

    if not site_message:
        site_message = create_site_message(
            show_message_at=timezone.now(), show_message_to=timezone.now()
        )

    (
        deviation_template,
        _created,
    ) = OpeningHoursDeviationTemplate.objects.update_or_create(
        name=name, description=description, site_message=site_message
    )

    return deviation_template
