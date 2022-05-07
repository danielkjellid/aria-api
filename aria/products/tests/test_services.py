import pytest
from model_bakery import baker

from aria.products.enums import ProductStatus
from aria.products.models import Product, ProductOption, Variant
from aria.products.services import (
    product_option_delete_related_variants,
    variant_create,
)

pytestmark = pytest.mark.django_db


class TestProductsServices:
    def test_variant_create_creates_variant(self, django_assert_max_num_queries):
        """
        Test that variants are created using the variant_create service.
        """

        new_variant = variant_create(
            name="New Variant",
        )

        assert new_variant.name == "New Variant"

        with pytest.raises(ValueError):
            variant_create(name="")

    def test_product_option_delete_related_variants_deletes_variants(
        self, django_assert_max_num_queries
    ):
        """
        Test that we delete dangling variants after deleting the parent
        product option.
        """

        product = baker.make(Product)

        product_option_1 = baker.make(ProductOption, **{"product": product})
        product_option_2 = baker.make(ProductOption, **{"product": product})
        product_option_3 = baker.make(ProductOption, **{"product": product})

        variant_1 = baker.make(Variant, **{"is_standard": False})
        variant_2 = baker.make(Variant, **{"is_standard": False})

        # Create two product options with the same variant to test
        # that we do NOT delete variant_1. We do not want to delete
        # it when other product options are using it.
        product_option_1.variant = variant_1
        product_option_1.save(update_fields=["variant"])

        product_option_2.variant = variant_1
        product_option_2.save(update_fields=["variant"])

        # Create a separate instance where we want to test that we
        # actually delete the variant.
        product_option_3.variant = variant_2
        product_option_3.save(update_fields=["variant"])

        with django_assert_max_num_queries(1):
            product_option_delete_related_variants(instance=product_option_1)
        with django_assert_max_num_queries(4):
            product_option_delete_related_variants(instance=product_option_3)

        # Assert that variant_1 wasn't deleted.
        assert Variant.objects.filter(id=variant_1.id).exists()

        # Assert that variant_2 was deleted.
        with pytest.raises(Variant.DoesNotExist):
            Variant.objects.get(id=variant_2.id)
