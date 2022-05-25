from django.urls import reverse


class TestPublicCoreEndpoints:
    def test_url_core_site_health_check_api(self):
        """
        Test reverse match of core_site_health_check_api endpoint.
        """
        url = reverse("api-1.0.0:core-health")
        assert url == "/api/core/health/"


class TestPrivateCoreEndpoints:
    pass
