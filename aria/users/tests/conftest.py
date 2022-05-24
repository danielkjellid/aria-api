from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.sites.models import Site

import pytest

###############
# Permissions #
###############


@pytest.fixture
def test_permissions(request):
    return [request.param]


@pytest.fixture
def site(settings):
    site, _ = Site.objects.get_or_create(domain="test.example.com", name="Test site")
    settings.SITE_ID = site.id
    return site


@pytest.fixture
def create_user_with_permissions(django_user_model, site):
    """
    Returns a factory creating users given permissions.
    """

    def _make_user(perms, email="testuser@example.com", **defaults):
        user = django_user_model.objects.update_or_create(
            email=email,
            password="supersecretpassword",
            **defaults,
        )[0]

        parsed_perms = []

        for perm in perms:
            parsed_perm = Permission.objects.filter(codename=perm)

            # If multiple codenames are found, add them all.
            if len(parsed_perm) > 1:
                parsed_perm = list(parsed_perm)
                parsed_perms.extend(parsed_perm)
            else:
                parsed_perms.append(parsed_perm[0])

        user.user_permissions.set(parsed_perms)
        user.site = site
        user.save()

        return user

    return _make_user


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def unprivileged_user(create_user_with_permissions):
    return create_user_with_permissions([])


@pytest.fixture
def unprivileged_staff_user(create_user_with_permissions):
    return create_user_with_permissions([], is_staff=True)


@pytest.fixture
def privileged_user(create_user_with_permissions, test_permissions):
    return create_user_with_permissions(
        test_permissions,
    )


@pytest.fixture
def privileged_staff_user(create_user_with_permissions, test_permissions):

    return create_user_with_permissions(test_permissions, is_staff=True)


@pytest.fixture
def superuser(create_user_with_permissions):
    return create_user_with_permissions([], is_superuser=True, is_staff=True)
