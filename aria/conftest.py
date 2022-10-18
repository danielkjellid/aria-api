from typing import Any

from django.test import Client

import pytest  # noqa

from aria.api_auth.services import token_pair_obtain_for_user
from aria.users.tests.conftest import *  # noqa: F403, F401


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def authenticated_unprivileged_client(unprivileged_user):
    tokens = token_pair_obtain_for_user(unprivileged_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_privileged_client(privileged_user):
    tokens = token_pair_obtain_for_user(privileged_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_unprivileged_staff_client(unprivileged_staff_user):
    tokens = token_pair_obtain_for_user(unprivileged_staff_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_privileged_staff_client(privileged_staff_user):
    tokens = token_pair_obtain_for_user(privileged_staff_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def authenticated_superuser_client(superuser):
    tokens = token_pair_obtain_for_user(superuser)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def assert_client_response_is_status_code(django_assert_max_num_queries):
    def _make_test_util(
        *,
        client: Client,
        endpoint: str,
        max_allowed_queries: int,
        method: str = "GET",
        payload: Any | None = None,
        expected_status_code: int = 401,
        content_type: str | None = "application/json",
    ):
        client_method = getattr(client, method.lower(), None)

        if client_method is None:
            raise NotImplemented("Requested method not implemented.")

        with django_assert_max_num_queries(max_allowed_queries):
            response = client_method(endpoint, data=payload, content_type=content_type)

        assert response.status_code == expected_status_code

        return response

    return _make_test_util
