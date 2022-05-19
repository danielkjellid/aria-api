import pytest
from django.test import Client
from aria.api_auth.services import token_pair_obtain_for_user
from aria.users.tests.conftest import *


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def n_authenticated_unprivileged_client(unprivileged_user):
    tokens = token_pair_obtain_for_user(unprivileged_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def n_authenticated_privileged_client(privileged_user):
    tokens = token_pair_obtain_for_user(privileged_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def n_authenticated_privileged_staff_client(privileged_staff_user):
    tokens = token_pair_obtain_for_user(privileged_staff_user)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client


@pytest.fixture
def n_authenticated_superuser_client(superuser):
    tokens = token_pair_obtain_for_user(superuser)
    client = Client(HTTP_AUTHORIZATION=f"Bearer {tokens.access_token}")

    return client
