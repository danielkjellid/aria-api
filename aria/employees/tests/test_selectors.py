from django.core.cache import cache

import pytest

from aria.core.tests.utils import create_site
from aria.employees.records import EmployeeInfoRecord
from aria.employees.selectors import (
    employees_active_list_for_site,
    employees_active_list_for_site_from_cache,
)
from aria.employees.tests.utils import create_employee_info
from aria.users.tests.utils import create_user

pytestmark = pytest.mark.django_db


class TestEmployeesSelectors:
    def test_employees_active_list_for_site(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the employees_active_list_for_site selector returns expected output
        within query limit.
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

        # Uses 1 query to get list of employees.
        with django_assert_max_num_queries(1):
            employee_active_list = employees_active_list_for_site(site_id=site_1.id)

        # Assert that only the two active associated with the correct site is retrieved.
        assert len(employee_active_list) == 2
        assert sorted(employee_active_list, key=lambda x: x.id) == [
            EmployeeInfoRecord(
                id=user_1_employee.id,
                user_id=user_1_employee.user_id,
                first_name=user_1.first_name,
                last_name=user_1.last_name,
                full_name=user_1_employee.full_name,
                company_email=user_1_employee.company_email,
                profile_picture=user_1_employee.profile_picture.url
                if user_1_employee.profile_picture
                else None,
                offers_appointments=user_1_employee.offers_appointments,
                display_in_team_section=user_1_employee.display_in_team_section,
                is_active=user_1_employee.is_active,
            ),
            EmployeeInfoRecord(
                id=user_2_employee.id,
                user_id=user_2_employee.user_id,
                first_name=user_2.first_name,
                last_name=user_2.last_name,
                full_name=user_2_employee.full_name,
                company_email=user_2_employee.company_email,
                profile_picture=user_2_employee.profile_picture.url
                if user_2_employee.profile_picture
                else None,
                offers_appointments=user_2_employee.offers_appointments,
                display_in_team_section=user_2_employee.display_in_team_section,
                is_active=user_2_employee.is_active,
            ),
        ]

    def test_employees_active_list_for_site_from_cache(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the employees_active_list_for_site_from_cache correctly returns from
        cache, and output is as expected, within query limits.
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

        cache.delete(f"employees.employee_list.site_id={site_1.id}")
        assert f"employees.employee_list.site_id={site_1.id}" not in cache

        # Uses 1 query to get list of employees.
        with django_assert_max_num_queries(1):
            employees_active_list_for_site_from_cache(site_id=site_1.id)

        # After first hit, instance should have been added to cache.
        assert f"employees.employee_list.site_id={site_1.id}" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            employees_active_list_for_site_from_cache(site_id=site_1.id)

        assert cache.get(f"employees.employee_list.site_id={site_1.id}") == [
            {
                "id": user_1_employee.id,
                "user_id": user_1_employee.user_id,
                "first_name": user_1_employee.first_name,
                "last_name": user_1_employee.last_name,
                "full_name": user_1_employee.full_name,
                "company_email": user_1_employee.company_email,
                "profile_picture": user_1_employee.profile_picture.url
                if user_1_employee.profile_picture
                else None,
                "offers_appointments": user_1_employee.offers_appointments,
                "display_in_team_section": user_1_employee.display_in_team_section,
                "is_active": user_1_employee.is_active,
            },
            {
                "id": user_2_employee.id,
                "user_id": user_2_employee.user_id,
                "first_name": user_2_employee.first_name,
                "last_name": user_2_employee.last_name,
                "full_name": user_2_employee.full_name,
                "company_email": user_2_employee.company_email,
                "profile_picture": user_2_employee.profile_picture.url
                if user_2_employee.profile_picture
                else None,
                "offers_appointments": user_2_employee.offers_appointments,
                "display_in_team_section": user_2_employee.display_in_team_section,
                "is_active": user_2_employee.is_active,
            },
        ]
