from django.urls import reverse


class TestPublicFrontUrls:
    def test_url_opening_hours_detail_api(self) -> None:
        """
        Test reverse match of opening_hours_detail_api endpoint.
        """
        url = reverse("api-1.0.0:front-opening-hours-{site_id}", args=["site_id"])

        assert url == "/api/front/opening-hours/site_id/"
