from typing import Optional, TypedDict


class WeekdaysByTimeSlotDict(TypedDict):
    time_slot: Optional[str]
    days: list[str]
    is_closed: bool


class TimeSlotByWeekdaysDict(TypedDict):
    days: str
    time_slot: Optional[str]
    is_closed: bool
