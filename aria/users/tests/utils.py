from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from aria.core.tests.utils import create_site
from aria.users.models import User


def create_user(  # pylint: disable=too-many-arguments
    first_name: str = "Test",
    last_name: str = "User",
    email: str = "user@example.com",
    password: str = "supersecret",
    site: Site | None = None,
    perms: list[str] | None = None,
    is_active: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
    street_address: str = "Test street 1",
    zip_code: str = "0172",
    zip_place: str = "Oslo",
    phone_number: str = "91812345",
    **defaults: Any,
) -> User:
    """
    Test utility for creating a user instance.
    """
    if site is None:
        site = create_site()

    user, _ = User.objects.update_or_create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
        street_address=street_address,
        zip_code=zip_code,
        zip_place=zip_place,
        phone_number=phone_number,
        **defaults,
    )

    parsed_perms = []
    if perms:
        content_type = ContentType.objects.get_for_model(User)

        for perm in perms:
            parsed_perm = Permission.objects.get(
                codename=perm, content_type=content_type
            )
            parsed_perms.append(parsed_perm)

    user.user_permissions.set(parsed_perms)
    user.site = site
    user.save()

    return user


def create_group(name: str = "Test group", perms: list[str] | None = None) -> Group:
    """
    Test utility for creating a group.
    """

    group, _created = Group.objects.update_or_create(name=name)

    parsed_perms = []
    if perms:
        content_type = ContentType.objects.get_for_model(User)

        for perm in perms:
            parsed_perm = Permission.objects.get(
                codename=perm, content_type=content_type
            )
            parsed_perms.append(parsed_perm)

    group.permissions.set(parsed_perms)
    group.save()

    return group
