from django.urls import reverse


class TestPublicEmployeesUrls:
    def test_url_employee_list_api(self) -> None:
        """
        Test reverse match of employee_list_api endpoint.
        """
        url = reverse("api-1.0.0:employees-{site_id}", args=["site_id"])

        assert url == "/api/employees/site_id/"
