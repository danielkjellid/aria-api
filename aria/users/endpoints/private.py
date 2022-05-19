from ninja import Router, Schema, Query
from django.utils.translation import gettext_lazy as _

from aria.api.decorators import api
from aria.api.responses import ExceptionResponse, GenericResponse
from aria.core.decorators import permission_required
from aria.users.selectors import user_list
from aria.api.decorators import paginate
from aria.users.schemas.outputs import UserListOutput, UserDetailOutput
from aria.users.schemas.inputs import UserUpdateInput
from aria.users.schemas.filters import UserListFilters
from rest_framework.generics import get_object_or_404
from aria.users.models import User
from aria.users.services import user_update

router = Router(tags="users")


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
@paginate(page_size=18, order_by="id")
# @permission_required("users.has_users_list")
def user_list_api(request, filters: UserListFilters = Query(...)):
    """
    Retrieve a list of all users in the application.
    """

    users = user_list(filters=filters.dict())
    return users


@api(
    router,
    "{user_id}/",
    method="GET",
    response={
        200: UserDetailOutput,
        403: ExceptionResponse,
        404: ExceptionResponse,
    },
    summary="Retrieve a single user",
)
# @permission_required("users.has_users_list")
def user_detail_api(request, user_id: int):
    """
    Retrieve a single user based on user id.
    """

    user = get_object_or_404(User, pk=user_id)
    return 200, user


@api(
    router,
    "{user_id}/update/",
    method="POST",
    response={200: GenericResponse, 403: ExceptionResponse, 404: ExceptionResponse},
    summary="Update a single user",
)
# @permission_required("users.has_user_edit")
def user_update_api(request, user_id: int, payload: UserUpdateInput):
    """
    Update a specific user based on user id.
    """

    user = get_object_or_404(User, pk=user_id)

    user_update(user=user, data=payload.dict(), author=request.auth, log_change=True)

    return 200, GenericResponse(message=_("User was updated successfully"), data={})
