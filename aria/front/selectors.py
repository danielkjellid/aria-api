from django.utils import timezone

from aria.front.models import OpeningHours
from aria.front.records import (
    OpeningHoursDeviationRecord,
    OpeningHoursDeviationTemplateRecord,
    OpeningHoursRecord,
    OpeningHoursTimeSlotRecord,
    SiteMessageRecord,
)


def site_message_active_list():
    pass


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

    return oh_record


def opening_hours_detail_formatted(site_id: int):
    record = opening_hours_detail(site_id=site_id)

    # test = [val for i, time_slot in enumerate(record.time_slots) for val in time_slot]
    test = []

    for time_slot in record.time_slots:
        for ts in record.time_slots:
            if time_slot.weekday == ts.weekday and (
                (
                    time_slot.opening_at == ts.opening_at
                    and time_slot.closing_at == ts.closing_at
                )
                or time_slot.is_closed == ts.is_closed
            ):

                time_slot_val = f"{time_slot.opening_at} - {time_slot.closing_at}"

                dict_instance = next(
                    (d for i, d in enumerate(test) if time_slot_val in d["time_slot"]),
                    None,
                )

                if dict_instance is None:

                    if (
                        not time_slot.opening_at
                        and not time_slot.closing_at
                        and time_slot.is_closed
                    ):
                        test.append(
                            {
                                "time_slot": None,
                                "days": [time_slot.weekday],
                                "is_closed": True,
                            }
                        )
                        continue
                    test.append(
                        {
                            "time_slot": time_slot_val,
                            "days": [time_slot.weekday],
                            "is_closed": False,
                        }
                    )
                    continue

                dict_instance["days"].append(time_slot.weekday)

    formatted_test = []

    for t in test:
        if len(t["days"]) > 1:
            first_day = t["days"][0]
            last_day = t["days"][len(t["days"]) - 1]

            formatted_test.append(
                {
                    "days": f"{first_day} - {last_day}",
                    "time_slot": t["time_slot"],
                    "is_closed": t["is_closed"],
                }
            )
        elif len(t["days"]) == 1:
            day = t["days"][0]
            formatted_test.append(
                {
                    "days": f"{day}",
                    "time_slot": t["time_slot"],
                    "is_closed": t["is_closed"],
                }
            )

    return formatted_test


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
