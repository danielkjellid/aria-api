from datetime import datetime
from typing import Optional

from ninja import Schema

from aria.front.enums import SiteMessageType


class OpeningHoursHumanReadableTimeSlotsOutputSchema(Schema):
    days: str
    time_slot: Optional[str]
    is_closed: bool


class OpeningHoursOutputSchema(Schema):
    id: int
    human_readable_time_slots: list[OpeningHoursHumanReadableTimeSlotsOutputSchema]


class SiteMessageOutputSchema(Schema):
    text: str
    message_type: SiteMessageType
    locations: list[str]
    show_message_at: datetime | None
    show_message_to: datetime | None
