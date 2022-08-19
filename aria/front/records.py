from datetime import datetime, time

from pydantic import BaseModel

from aria.front.enums import SiteMessageType


class SiteMessageRecord(BaseModel):
    id: int
    text: str
    message_type: SiteMessageType
    locations: list[str]
    show_message_at: datetime | None
    show_message_to: datetime | None


class OpeningHoursTimeSlotRecord(BaseModel):
    id: int
    weekday: str
    opening_at: time | None
    closing_at: time | None
    is_closed: bool | None = False


class OpeningHoursTimeSlotHumanReadableRecord(BaseModel):
    days: str
    time_slot: str | None = None
    is_closed: bool


class OpeningHoursRecord(BaseModel):
    id: int
    time_slots: list[OpeningHoursTimeSlotRecord]
    human_readable_time_slots: list[OpeningHoursTimeSlotHumanReadableRecord]


class OpeningHoursDeviationTemplateRecord(BaseModel):
    id: int
    name: str
    description: str
    site_message: SiteMessageRecord | None


class OpeningHoursDeviationRecord(BaseModel):
    id: int
    opening_hours_id: int
    template: OpeningHoursDeviationTemplateRecord | None
    active_at: datetime
    active_to: datetime
    description: str
    disable_appointment_bookings: bool
    time_slots: list[OpeningHoursTimeSlotRecord]
