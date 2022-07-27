from pydantic import BaseModel

from aria.core.records import SiteRecord


class EmployeeInfoRecord(BaseModel):
    user_id: int

    first_name: str
    last_name: str
    full_name: str
    company_email: str
    profile_picture: str | None

    offers_appointments: bool
    display_in_team_section: bool

    site: SiteRecord
