import json

import pytest

from aria.employees.tests.utils import create_employee_info
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestPublicEmployeeEndpoints:

    BASE_ENDPOINT = "/api/v1/employees"

    def test_employee_list_api(
        self, django_assert_max_num_queries, anonymous_client
    ) -> None:
        """
        Test retrieving employees from an anonymous client returns
        a valid response.
        """

        user_1 = create_user(email="user_1@example.com")
        user_2 = create_user(email="user_2@example.com")
        user_3 = create_user(email="user_3@example.com")

        user_1_employee = create_employee_info(
            user=user_1, company_email="user_1@company.com", is_active=True
        )
        user_2_employee = create_employee_info(
            user=user_2, company_email="user_2@company.com", is_active=True
        )
        create_employee_info(
            user=user_3, company_email="user_3@company.com", is_active=False
        )

        expected_response = [
            {
                "fullName": user_1_employee.full_name,
                "companyEmail": user_1_employee.company_email,
                "profilePicture": user_1_employee.profile_picture.url
                if user_1_employee.profile_picture
                else None,
            },
            {
                "fullName": user_2_employee.full_name,
                "companyEmail": user_2_employee.company_email,
                "profilePicture": user_2_employee.profile_picture.url
                if user_2_employee.profile_picture
                else None,
            },
        ]

        # Uses 1 query for getting employees.
        with django_assert_max_num_queries(1):
            response = anonymous_client.get(f"{self.BASE_ENDPOINT}/")

        actual_response = json.loads(response.content)

        assert response.status_code == 200
        assert actual_response == expected_response
