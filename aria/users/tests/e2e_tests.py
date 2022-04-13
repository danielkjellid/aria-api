import pytest

pytestmark = pytest.mark.django_db


class TestUsersEndpoints:

    endpoint = "/api/users/"

    def test_unauthenticated_list(self, unauthenticated_client):
        response = unauthenticated_client().get(self.endpoint)

        assert response.status_code == 401
