from typing import Optional

from ninja import Schema


class OpeningHoursHumanReadableTimeSlotsOutputSchema(Schema):
    days: str
    time_slot: Optional[str]
    is_closed: bool


class OpeningHoursOutputSchema(Schema):
    id: int
    human_readable_time_slots: list[OpeningHoursHumanReadableTimeSlotsOutputSchema]
