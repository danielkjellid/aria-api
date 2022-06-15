from django.utils import timezone

from aria.front.models import OpeningHours, OpeningHoursTimeSlot
from aria.front.records import (
    OpeningHoursDeviationRecord,
    OpeningHoursDeviationTemplateRecord,
    OpeningHoursRecord,
    OpeningHoursTimeSlotHumanReadableRecord,
    OpeningHoursTimeSlotRecord,
    SiteMessageRecord,
)
from aria.front.types import TimeSlotByWeekdaysDict, WeekdaysByTimeSlotDict


def site_message_active_list():
    pass


def _opening_hours_weekdays_by_time_slot(
    time_slots: OpeningHoursTimeSlot | OpeningHoursTimeSlotRecord,
) -> list[WeekdaysByTimeSlotDict]:
    weekdays_by_timeslot: list[WeekdaysByTimeSlotDict] = []

    # Iterate over time slots matching them with all other time sliots in the list.
    for time_slot in time_slots:
        for ts in time_slots:
            # Group on weekday and matching opening/closing hours, or if it's closed.
            if (
                time_slot.weekday == ts.weekday
                and time_slot.opening_at is not None
                and time_slot.closing_at is not None
                and (
                    time_slot.opening_at == ts.opening_at
                    and time_slot.closing_at == ts.closing_at
                )
                and time_slot.is_closed is False
                and ts.is_closed is False
            ):

                time_slot_to_human_readable = f"{time_slot.opening_at.strftime('%H:%M')} - {time_slot.closing_at.strftime('%H:%M')}"

                # Iterate over the dict, getting the time_slot value.
                existing_dict_instance = next(
                    (
                        d
                        for i, d in enumerate(weekdays_by_timeslot)
                        if time_slot_to_human_readable in d["time_slot"]
                    ),
                    None,
                )

                # If the dict does not already exist, create a new dict instance.
                if existing_dict_instance is None:
                    weekdays_by_timeslot.append(
                        {
                            "time_slot": time_slot_to_human_readable,
                            "days": [time_slot.weekday],
                            "is_closed": False,
                        }
                    )
                    continue
                # If it exist, append weekday to dict instance.
                existing_dict_instance["days"].append(time_slot.weekday)

            elif (
                time_slot.weekday == ts.weekday and time_slot.is_closed == ts.is_closed
            ):
                existing_dict_instance = next(
                    (
                        d
                        for i, d in enumerate(weekdays_by_timeslot)
                        if d["is_closed"] is True
                    ),
                    None,
                )

                if existing_dict_instance is None:
                    weekdays_by_timeslot.append(
                        {
                            "time_slot": None,
                            "days": [time_slot.weekday],
                            "is_closed": True,
                        }
                    )
                    continue
                # If it exist, append weekday to dict instance.
                existing_dict_instance["days"].append(time_slot.weekday)
    return weekdays_by_timeslot


def _opening_hours_time_slot_by_weekdays(
    *, weekdays_by_time_slots: list[WeekdaysByTimeSlotDict]
) -> OpeningHoursTimeSlotHumanReadableRecord:
    time_slot_by_weekday: list[TimeSlotByWeekdaysDict] = []
    print(weekdays_by_time_slots)
    for obj in weekdays_by_time_slots:
        obj_days = obj["days"]
        obj_days_len = len(obj_days)
        time_slot = obj["time_slot"]
        is_closed = obj["is_closed"]

        first_day = f"{obj_days[0]}"

        if obj_days_len > 1:
            last_day = f"{obj_days[obj_days_len - 1]}"

            time_slot_by_weekday.append(
                {
                    "days": f"{first_day} - {last_day}",
                    "time_slot": f"{time_slot}",
                    "is_closed": f"{is_closed}",
                }
            )
        elif obj_days_len == 1:
            time_slot_by_weekday.append(
                {
                    "days": f"{first_day}",
                    "time_slot": time_slot,
                    "is_closed": is_closed,
                }
            )

    return [
        OpeningHoursTimeSlotHumanReadableRecord(
            days=obj["days"], time_slot=obj["time_slot"], is_closed=obj["is_closed"]
        )
        for obj in time_slot_by_weekday
    ]


def _opening_hours_time_slots_merge_to_human_readable(
    time_slots: OpeningHoursTimeSlot | OpeningHoursTimeSlotRecord,
):

    weekdays_by_timeslot = _opening_hours_weekdays_by_time_slot(time_slots=time_slots)
    time_slot_by_weekday = _opening_hours_time_slot_by_weekdays(
        weekdays_by_time_slots=weekdays_by_timeslot
    )

    return time_slot_by_weekday


def opening_hours_detail(site_id: int) -> OpeningHoursRecord:
    opening_hours_obj = (
        OpeningHours.objects.filter(site_id=site_id)
        .prefetch_related("time_slots")
        .with_active_deviations()
        .first()
    )

    oh_record = opening_hours_record(opening_hours=opening_hours_obj)

    if len(opening_hours_obj.active_deviations) > 0:
        opening_hours_deviation_record = deviation_record_for_opening_hours(
            opening_hours=opening_hours_obj
        )

        for i, time_slot in enumerate(oh_record.time_slots):
            for deviation_time_slot in opening_hours_deviation_record.time_slots:
                if time_slot.weekday == deviation_time_slot.weekday:
                    oh_record.time_slots[i] = deviation_time_slot

        oh_record.human_readable_time_slots = (
            _opening_hours_time_slots_merge_to_human_readable(
                time_slots=oh_record.time_slots
            )
        )

    return oh_record


def opening_hours_record(opening_hours: OpeningHours):
    return OpeningHoursRecord(
        id=opening_hours.id,
        site_id=opening_hours.site_id,
        time_slots=[
            OpeningHoursTimeSlotRecord(
                id=time_slot.id,
                weekday=time_slot.weekday,
                opening_at=time_slot.opening_at if time_slot.opening_at else None,
                closing_at=time_slot.closing_at if time_slot.closing_at else None,
                is_closed=time_slot.is_closed if time_slot.is_closed else None,
            )
            for time_slot in opening_hours.time_slots.all()
        ],
        human_readable_time_slots=_opening_hours_time_slots_merge_to_human_readable(
            time_slots=opening_hours.time_slots.all()
        ),
    )


def deviation_record_for_opening_hours(
    opening_hours: OpeningHours,
) -> OpeningHoursDeviationRecord:

    prefetched_active_deviations = getattr(opening_hours, "active_deviations", None)

    if prefetched_active_deviations is not None:
        active_deviation = prefetched_active_deviations[0]
    else:
        active_deviation = (
            opening_hours.deviations.filter(
                active_at__lte=timezone.now(), active_to__gt=timezone.now()
            )
            .prefetch_related("time_slots", "template__site_message__locations")
            .select_related("template", "template__site_message")
            .first()
        )

    return OpeningHoursDeviationRecord(
        id=active_deviation.id,
        opening_hours_id=opening_hours.id,
        template=OpeningHoursDeviationTemplateRecord(
            id=active_deviation.template.id,
            name=active_deviation.template.name,
            description=active_deviation.template.description,
            site_message=SiteMessageRecord(
                id=active_deviation.template.site_message.id,
                text=active_deviation.template.site_message.text,
                message_type=active_deviation.template.site_message.message_type,
                locations=[
                    location.slug
                    for location in active_deviation.template.site_message.locations.all()
                ],
                site_id=active_deviation.template.site_message.site_id,
                show_message_at=active_deviation.template.site_message.show_message_at,
                show_message_to=active_deviation.template.site_message.show_message_to,
            )
            if active_deviation.template.site_message
            else None,
        )
        if active_deviation.template
        else None,
        active_at=active_deviation.active_at,
        active_to=active_deviation.active_to,
        description=active_deviation.description,
        disable_appointment_bookings=active_deviation.disable_appointment_bookings,
        time_slots=[
            OpeningHoursTimeSlotRecord(
                id=time_slot.id,
                weekday=time_slot.weekday,
                opening_at=time_slot.opening_at if time_slot.opening_at else None,
                closing_at=time_slot.closing_at if time_slot.closing_at else None,
                is_closed=time_slot.is_closed if time_slot.is_closed else None,
            )
            for time_slot in active_deviation.time_slots.all()
        ],
    )
