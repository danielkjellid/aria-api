from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIClient

import pytest


@pytest.fixture
def test_permission():
    return "test-permission"


@pytest.fixture
def make_user_with_permissions(django_user_model):
    """
    Returns a factory creating users given permissions.
    """

    def _make_user(perms, email="test@example.com", **defaults):
        user = django_user_model.objects.update_or_create(email=email, **defaults)
        user.user_permissions.add(perms)

    return _make_user


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def inactive_user(make_user_with_permissions, test_permission):
    return make_user_with_permissions([test_permission], is_active=False)


@pytest.fixture
def unprivileged_user(make_user_with_permissions):
    return make_user_with_permissions([])


@pytest.fixture
def privileged_user(make_user_with_permissions, test_permission):
    return make_user_with_permissions([test_permission])


@pytest.fixture
def superuser(make_user_with_permissions):
    return make_user_with_permissions([], is_superuser=True)


@pytest.fixture
def make_user_request(rf):
    def _make_request(user, path="/path"):
        request = rf.get(path)
        request.user = user
        return request

    return _make_request


@pytest.fixture
def unauthenticated_client():
    return APIClient


@pytest.fixture
def authenticated_client(settings):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {settings.INTERNAL_AUTH_TOKEN}")
    return client
