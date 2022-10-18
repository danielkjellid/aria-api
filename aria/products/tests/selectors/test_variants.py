import pytest

from aria.products.records import ProductVariantRecord
from aria.products.selectors.variants import variant_list
from aria.products.tests.utils import create_variant

pytestmark = pytest.mark.django_db


class TestProductVariantsSelectors:
    def test_selector_variant_list(self, django_assert_max_num_queries):
        """
        Test that the variant_list selector returns expected output withing query
        limits.
        """

        variant_1 = create_variant(name="Variant 1", is_standard=False)
        variant_2 = create_variant(name="Variant 2", is_standard=False)
        variant_3 = create_variant(name="Variant 3", is_standard=True)
        variant_4 = create_variant(name="Variant 4", is_standard=False)

        expected_output = [
            ProductVariantRecord(
                id=variant_4.id,
                name="Variant 4",
                is_standard=False,
                image=variant_4.image.url if variant_4.image else None,
                thumbnail=variant_4.thumbnail.url if variant_4.thumbnail else None,
            ),
            ProductVariantRecord(
                id=variant_3.id,
                name="Variant 3",
                is_standard=True,
                image=variant_3.image.url if variant_3.image else None,
                thumbnail=variant_3.thumbnail.url if variant_3.thumbnail else None,
            ),
            ProductVariantRecord(
                id=variant_2.id,
                name="Variant 2",
                is_standard=False,
                image=variant_2.image.url if variant_2.image else None,
                thumbnail=variant_2.thumbnail.url if variant_2.thumbnail else None,
            ),
            ProductVariantRecord(
                id=variant_1.id,
                name="Variant 1",
                is_standard=False,
                image=variant_1.image.url if variant_1.image else None,
                thumbnail=variant_1.thumbnail.url if variant_1.thumbnail else None,
            ),
        ]

        with django_assert_max_num_queries(1):
            variants = variant_list()

        assert variants == expected_output
