from django.contrib.auth.models import AnonymousUser, Permission

import pytest

###############
# Permissions #
###############


@pytest.fixture
def test_permissions(request):
    try:
        return [request.param]
    except AttributeError:
        return []


@pytest.fixture
def create_user_with_permissions(django_user_model):
    """
    Returns a factory creating users given permissions.
    """

    def _make_user(perms, email="testuser@example.com", **defaults):
        user = django_user_model.objects.update_or_create(
            email=email,
            password="supersecretpassword",
            **defaults,
        )[0]

        parsed_perms: list[Permission] = []

        for perm in perms:
            parsed_perm = Permission.objects.filter(codename=perm)

            # If multiple codenames are found, add them all.
            if len(parsed_perm) > 1:
                parsed_perm = list(parsed_perm)  # type: ignore
                parsed_perms.extend(parsed_perm)
            else:
                parsed_perms.append(parsed_perm[0])

        user.user_permissions.set(parsed_perms)
        user.save()

        return user

    return _make_user


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def unprivileged_user(create_user_with_permissions):
    return create_user_with_permissions([], email="unprivileged_user@example.com")


@pytest.fixture
def unprivileged_staff_user(create_user_with_permissions):
    return create_user_with_permissions(
        [], email="unprivileged_staff_user@example.com", is_staff=True
    )


@pytest.fixture
def privileged_user(create_user_with_permissions, test_permissions):
    return create_user_with_permissions(
        test_permissions, email="privileged_user@example.com"
    )


@pytest.fixture
def privileged_staff_user(create_user_with_permissions, test_permissions):

    return create_user_with_permissions(
        test_permissions, email="privileged_staff_user@example.com", is_staff=True
    )


@pytest.fixture
def superuser(create_user_with_permissions):
    return create_user_with_permissions(
        [], email="superuser@example.com", is_superuser=True, is_staff=True
    )
