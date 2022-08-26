from datetime import datetime

from ninja import Schema

from aria.front.enums import SiteMessageType


class OpeningHoursHumanReadableTimeSlotsOutput(Schema):
    days: str
    time_slot: str | None
    is_closed: bool


class OpeningHoursOutput(Schema):
    id: int
    human_readable_time_slots: list[OpeningHoursHumanReadableTimeSlotsOutput]


class SiteMessageOutput(Schema):
    text: str
    message_type: SiteMessageType
    locations: list[str]
    show_message_at: datetime | None
    show_message_to: datetime | None
