import pytest

from aria.products.services.variants import variant_create

pytestmark = pytest.mark.django_db


class TestProductVariantsServices:
    def test_service_variant_create(self, django_assert_max_num_queries):
        """
        Test that variants are created using the variant_create service.
        """

        with django_assert_max_num_queries(1):
            new_variant = variant_create(
                name="New Variant",
            )

        assert new_variant.name == "New Variant"

        with pytest.raises(AssertionError):
            variant_create(name="")
