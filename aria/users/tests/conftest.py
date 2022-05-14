from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from rest_framework.test import APIClient

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

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
        content_type = ContentType.objects.get_for_model(django_user_model)

        for perm in perms:
            parsed_perm = Permission.objects.get(
                codename=perm, content_type=content_type
            )
            parsed_perms.append(parsed_perm)

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


###############
# API Clients #
###############


@pytest.fixture
def unauthenticated_client():
    return APIClient()


@pytest.fixture
def authenticated_unprivileged_client(unprivileged_user):
    client = APIClient()
    tokens = RefreshToken.for_user(unprivileged_user)
    client.credentials(HTTP_AUTHORIZATION=f"JWT {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_privileged_client(privileged_user):
    client = APIClient()
    tokens = RefreshToken.for_user(privileged_user)
    client.credentials(HTTP_AUTHORIZATION=f"JWT {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_privileged_staff_client(privileged_staff_user):
    client = APIClient()
    tokens = RefreshToken.for_user(privileged_staff_user)
    client.credentials(HTTP_AUTHORIZATION=f"JWT {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_superuser_client(superuser):
    client = APIClient()
    tokens = RefreshToken.for_user(superuser)
    client.credentials(HTTP_AUTHORIZATION=f"JWT {tokens.access_token}")

    return client
