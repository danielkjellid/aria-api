from ninja import Router, Schema, Query
from ninja.pagination import paginate, PageNumberPagination
from aria.api.decorators import api
from aria.api.responses import GenericResponse
from aria.core.decorators import permission_required
from aria.users.selectors import user_list
from datetime import datetime

router = Router(tags="users")


class UserListFilters(Schema):
    email: str = None
    first_name: str = None
    last_name: str = None
    phone_number: str = None


class UserListProfileOutput(Schema):
    full_name: str
    initial: str
    avatar_color: str


class UserListOutput(Schema):
    id: int
    email: str
    is_active: bool
    date_joined: datetime
    full_name: str
    initial: str
    avatar_color: str


@api(
    router,
    "/",
    method="GET",
    response={200: list[UserListOutput]},
    summary="Lists all users",
    description="Retrieve a list of all users in the application.",
)
# @permission_required("users.has_users_list")
@paginate(PageNumberPagination, page_size=18)
def user_list_api(request, filters: UserListFilters = Query(...)):
    users = user_list(filters=filters.dict())
    return users
