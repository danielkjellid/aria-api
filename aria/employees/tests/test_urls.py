from django.urls import reverse


class TestPublicEmployeesUrls:
    def test_url_employee_list_api(self) -> None:
        """
        Test reverse match of employee_list_api endpoint.
        """
        url = reverse("api-public-1.0.0:employees-index")

        assert url == "/api/v1/employees/"
