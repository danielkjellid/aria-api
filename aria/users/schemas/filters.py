from ninja import Schema


class UserListFilters(Schema):
    email: str = None
    first_name: str = None
    last_name: str = None
    phone_number: str = None
