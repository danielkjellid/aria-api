import json

import pytest

from aria.core.tests.utils import create_site
from aria.employees.tests.utils import create_employee_info
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestPublicEmployeeEndpoints:

    BASE_ENDPOINT = "/api/employees"

    def test_employee_list_api(
        self, django_assert_max_num_queries, anonymous_client
    ) -> None:
        """
        Test retrieving employees for a site from an anonymous client returns
        a valid response.
        """

        site_1 = create_site()
        site_2 = create_site(site_id=999, domain="example-2.com", name="Example 2")

        user_1 = create_user(email="user_1@example.com", site=site_1)
        user_2 = create_user(email="user_2@example.com", site=site_1)
        user_3 = create_user(email="user_3@example.com", site=site_1)
        user_4 = create_user(email="user_4@example.com", site=site_2)

        user_1_employee = create_employee_info(
            user=user_1, company_email="user_1@company.com", is_active=True
        )
        user_2_employee = create_employee_info(
            user=user_2, company_email="user_2@company.com", is_active=True
        )
        create_employee_info(
            user=user_3, company_email="user_3@company.com", is_active=False
        )
        create_employee_info(
            user=user_4, company_email="user_4@company.com", is_active=True
        )

        expected_response = [
            {
                "full_name": user_1_employee.full_name,
                "company_email": user_1_employee.company_email,
                "profile_picture": user_1_employee.profile_picture.url
                if user_1_employee.profile_picture
                else None,
            },
            {
                "full_name": user_2_employee.full_name,
                "company_email": user_2_employee.company_email,
                "profile_picture": user_2_employee.profile_picture.url
                if user_2_employee.profile_picture
                else None,
            },
        ]

        # Uses 1 query for getting employees.
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/{site_1.id}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
