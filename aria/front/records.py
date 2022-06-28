from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel

from aria.front.enums import SiteMessageType


class SiteMessageRecord(BaseModel):
    id: int
    text: str
    message_type: SiteMessageType
    locations: list[str]
    site_id: int
    show_message_at: datetime | None
    show_message_to: datetime | None


class OpeningHoursTimeSlotRecord(BaseModel):
    id: int
    weekday: str
    opening_at: Optional[time]
    closing_at: Optional[time]
    is_closed: Optional[bool] = False


class OpeningHoursTimeSlotHumanReadableRecord(BaseModel):
    days: str
    time_slot: Optional[str] = None
    is_closed: bool


class OpeningHoursRecord(BaseModel):
    id: int
    site_id: int
    time_slots: list[OpeningHoursTimeSlotRecord]
    human_readable_time_slots: list[OpeningHoursTimeSlotHumanReadableRecord]


class OpeningHoursDeviationTemplateRecord(BaseModel):
    id: int
    name: str
    description: str
    site_message: Optional[SiteMessageRecord]


class OpeningHoursDeviationRecord(BaseModel):
    id: int
    opening_hours_id: int
    template: Optional[OpeningHoursDeviationTemplateRecord]
    active_at: datetime
    active_to: datetime
    description: str
    disable_appointment_bookings: bool
    time_slots: list[OpeningHoursTimeSlotRecord]
