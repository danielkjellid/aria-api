from typing import Any

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from aria.core.tests.utils import create_site
from aria.users.models import User


def create_user(
    email: str = "user@example.com",
    password: str = "supersecret",
    site: Site | None = None,
    perms: list[str] | None = None,
    is_active: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
    **defaults: Any,
) -> User:

    if site is None:
        site = create_site()

    user, _ = User.objects.update_or_create(
        email=email,
        password=password,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
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
