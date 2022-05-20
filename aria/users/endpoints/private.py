from rest_framework.generics import get_object_or_404

from ninja import Query, Router

from aria.api.decorators import api, paginate
from aria.api.responses import codes_40x
from aria.api.schemas.responses import ExceptionResponse
from aria.api_auth.decorators import permission_required
from aria.users.models import User
from aria.users.schemas.filters import UserListFilters
from aria.users.schemas.inputs import UserUpdateInput
from aria.users.schemas.outputs import UserDetailOutput, UserListOutput
from aria.users.selectors import user_list
from aria.users.services import user_update

router = Router(tags="users")


@api(
    router,
    "/",
    method="GET",
    response={
        200: list[UserListOutput],
        codes_40x: ExceptionResponse,
    },
    summary="Lists all users",
)
@paginate(page_size=18, order_by="id")
@permission_required("users.has_users_list")
def user_list_api(
    request, filters: UserListFilters = Query(...)
) -> list[UserListOutput]:
    """
    Retrieve a list of all users in the application.
    """

    users = user_list(filters=filters.dict())
    return users


@api(
    router,
    "{user_id}/",
    method="GET",
    response={200: UserDetailOutput, codes_40x: ExceptionResponse},
    summary="Retrieve a single user",
)
@permission_required("users.has_users_list")
def user_detail_api(request, user_id: int) -> tuple[int, User]:
    """
    Retrieve a single user based on user id.
    """

    user = get_object_or_404(User, pk=user_id)
    return 200, user


@api(
    router,
    "{user_id}/update/",
    method="POST",
    response={200: None, codes_40x: ExceptionResponse},
    summary="Update a single user",
)
@permission_required("users.has_user_edit")
def user_update_api(request, user_id: int, payload: UserUpdateInput) -> int:
    """
    Update a specific user based on user id.
    """

    user = get_object_or_404(User, pk=user_id)

    # Remove None values from dict, as all fields in input schema is optional.
    cleaned_payload = {
        key: val for key, val in payload.dict().items() if val is not None
    }

    user_update(user=user, data=cleaned_payload, author=request.auth, log_change=True)

    return 200
