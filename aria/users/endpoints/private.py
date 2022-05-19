from ninja import Router, Schema, Query
from aria.api.decorators import api
from aria.api.responses import ExceptionResponse
from aria.core.decorators import permission_required
from aria.users.selectors import user_list
from datetime import datetime
from aria.api.decorators import paginate

router = Router(tags="users")


class UserListFilters(Schema):
    email: str = None
    first_name: str = None
    last_name: str = None
    phone_number: str = None


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
    response={
        200: list[UserListOutput],
        403: ExceptionResponse,
        404: ExceptionResponse,
    },
    summary="Lists all users",
)
@paginate(page_size=2, order_by="id")
# @permission_required("users.has_users_list")
def user_list_api(request, filters: UserListFilters = Query(...)):
    """
    Retrieve a list of all users in the application.
    """

    users = user_list(filters=filters.dict())
    return users
