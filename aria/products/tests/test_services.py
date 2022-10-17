import pytest

from aria.products.models import Variant
from aria.products.services.product_options import (
    product_option_delete_related_variants,
)
from aria.products.services.variants import variant_create
from aria.products.tests.utils import (
    create_product,
    create_product_option,
    create_variant,
)

pytestmark = pytest.mark.django_db


class TestProductsServices:
    def test_variant_create_creates_variant(self) -> None:
        """
        Test that variants are created using the variant_create service.
        """

        new_variant = variant_create(
            name="New Variant",
        )

        assert new_variant.name == "New Variant"

        with pytest.raises(AssertionError):
            variant_create(name="")
