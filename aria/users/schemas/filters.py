from ninja import Schema


class UserListFilters(Schema):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
