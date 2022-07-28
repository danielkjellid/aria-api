from ninja import Schema


class EmployeeListOutput(Schema):
    full_name: str
    company_email: str
    profile_picture: str | None
