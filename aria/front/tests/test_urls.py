from django.urls import reverse


class TestPublicFrontUrls:
    def test_url_opening_hours_detail_api(self) -> None:
        """
        Test reverse match of opening_hours_detail_api endpoint.
        """
        url = reverse("api-1.0.0:front-opening-hours")

        assert url == "/api/front/opening-hours/"

    def test_url_site_messages_active_list_api(self) -> None:
        """
        Test reverse match of site_messages_active_list_api endpoint.
        """
        url = reverse("api-1.0.0:front-site-messages-active")

        assert url == "/api/front/site-messages/active/"
