from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

import pytest

from aria.discounts.records import DiscountRecord
from aria.discounts.selectors import (
    discount_active_list,
    discount_active_list_from_cache,
)
from aria.discounts.tests.utils import create_discount
from aria.product_attributes.records import VariantDetailRecord
from aria.products.models import Product
from aria.products.records import (
    ProductColorRecord,
    ProductDiscountRecord,
    ProductListRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
)
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestDiscountsSelectors:
    def test_selector_discount_active_list(self, django_assert_max_num_queries):
        """
        Test that the discount_active_list selector returns expected output
        withing query limits.
        """

        product_1 = create_product(product_name="Product 1")

        product_2 = create_product(product_name="Product 2")
        product_2_option_1 = create_product_option(product=product_2)

        product_3 = create_product(product_name="Product 3")
        product_4 = create_product(product_name="Product 4")

        active_discount_1 = create_discount(
            name="Discount 1 20%",
            products=[product_1, product_4],
            product_options=[product_2_option_1],
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=1,
        )
        active_discount_2 = create_discount(
            name="Discount 2 40%",
            products=[product_3],
            discount_gross_percentage=Decimal("0.40"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=2,
        )
        active_discount_3 = create_discount(
            name="Discount 3 200NOK",
            products=[product_2],
            discount_gross_price=Decimal("200.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=3,
        )
        expired_discount_1 = create_discount(
            name="Expired discount 1",
            products=[product_1],
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now() - timedelta(days=2),
            active_to=timezone.now() - timedelta(days=1),
            ordering=4,
        )

        def _product_record(product: Product, **kwargs) -> ProductListRecord:
            return ProductListRecord(
                id=product.id,
                name=product.name,
                slug=product.slug,
                status=product.status_display,
                unit=product.unit_display,
                supplier=ProductSupplierRecord(
                    id=product.supplier_id,
                    name=product.supplier.name,
                    origin_country=product.supplier.country_name,
                    origin_country_flag=product.supplier.unicode_flag,
                ),
                thumbnail=product.thumbnail.url if product.thumbnail else None,
                display_price=product.display_price,
                from_price=product.from_price,
                materials=product.materials_display,
                rooms=product.rooms_display,
                colors=[
                    ProductColorRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product.colors.all()
                ],
                shapes=[
                    ProductShapeRecord(
                        id=shape.id, name=shape.name, image=shape.image.url
                    )
                    for shape in product.shapes.all()
                ],
                variants=[
                    VariantDetailRecord(
                        id=option.variant.id,
                        name=option.variant.name,
                        image=option.variant.image.url
                        if option.variant.image
                        else None,
                        thumbnail=option.variant.thumbnail.url
                        if option.variant.thumbnail
                        else None,
                        is_standard=option.variant.is_standard,
                    )
                    for option in product.options.available()
                    if option.variant
                ],
                **kwargs,
            )

        # Uses 11 queries.
        with django_assert_max_num_queries(11):
            active_discounts = discount_active_list()

        assert len(active_discounts) == 3
        assert expired_discount_1 not in active_discounts
        assert active_discounts == [
            DiscountRecord(
                id=active_discount_1.id,
                name=active_discount_1.name,
                description=active_discount_1.description,
                slug=active_discount_1.slug,
                products=[
                    _product_record(
                        product=product_4,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                    _product_record(
                        product=product_2_option_1.product,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                    _product_record(
                        product=product_1,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                ],
                minimum_quantity=active_discount_1.minimum_quantity,
                maximum_quantity=active_discount_1.maximum_quantity,
                discount_gross_price=active_discount_1.discount_gross_price,
                discount_gross_percentage=active_discount_1.discount_gross_percentage,
                maximum_sold_quantity=active_discount_1.maximum_sold_quantity,
                total_sold_quantity=active_discount_1.total_sold_quantity,
                display_maximum_quantity=active_discount_1.display_maximum_quantity,
                active_at=active_discount_1.active_at,
                active_to=active_discount_1.active_to,
                ordering=active_discount_1.ordering,
            ),
            DiscountRecord(
                id=active_discount_2.id,
                name=active_discount_2.name,
                description=active_discount_2.description,
                slug=active_discount_2.slug,
                products=[
                    _product_record(
                        product=product_3,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("120.00"),
                            discounted_gross_percentage=Decimal("0.40"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    )
                ],
                minimum_quantity=active_discount_2.minimum_quantity,
                maximum_quantity=active_discount_2.maximum_quantity,
                discount_gross_price=active_discount_2.discount_gross_price,
                discount_gross_percentage=active_discount_2.discount_gross_percentage,
                maximum_sold_quantity=active_discount_2.maximum_sold_quantity,
                total_sold_quantity=active_discount_2.total_sold_quantity,
                display_maximum_quantity=active_discount_2.display_maximum_quantity,
                active_at=active_discount_2.active_at,
                active_to=active_discount_2.active_to,
                ordering=active_discount_2.ordering,
            ),
            DiscountRecord(
                id=active_discount_3.id,
                name=active_discount_3.name,
                description=active_discount_3.description,
                slug=active_discount_3.slug,
                products=[
                    _product_record(
                        product=product_2,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("200.00"),
                            discounted_gross_percentage=None,
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    )
                ],
                minimum_quantity=active_discount_3.minimum_quantity,
                maximum_quantity=active_discount_3.maximum_quantity,
                discount_gross_price=active_discount_3.discount_gross_price,
                discount_gross_percentage=active_discount_3.discount_gross_percentage,
                maximum_sold_quantity=active_discount_3.maximum_sold_quantity,
                total_sold_quantity=active_discount_3.total_sold_quantity,
                display_maximum_quantity=active_discount_3.display_maximum_quantity,
                active_at=active_discount_3.active_at,
                active_to=active_discount_3.active_to,
                ordering=active_discount_3.ordering,
            ),
        ]

    def test_selector_discount_active_list_from_cache(
        self, django_assert_max_num_queries
    ):
        """
        Test that the discount_active_list_from_cache selector returns expected output
        withing query limits from cache.
        """

        product_1 = create_product(product_name="Product 1")

        product_2 = create_product(product_name="Product 2")
        product_2_option_1 = create_product_option(product=product_2)

        product_3 = create_product(product_name="Product 3")
        product_4 = create_product(product_name="Product 4")

        active_discount_1 = create_discount(
            name="Discount 1 20%",
            products=[product_1, product_4],
            product_options=[product_2_option_1],
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=1,
        )
        active_discount_2 = create_discount(
            name="Discount 2 40%",
            products=[product_3],
            discount_gross_percentage=Decimal("0.40"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=2,
        )
        active_discount_3 = create_discount(
            name="Discount 3 200NOK",
            products=[product_2],
            discount_gross_price=Decimal("200.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
            ordering=3,
        )
        expired_discount_1 = create_discount(
            name="Expired discount 1",
            products=[product_1],
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now() - timedelta(days=2),
            active_to=timezone.now() - timedelta(days=1),
            ordering=4,
        )

        cache.delete("discounts.active")
        assert "discounts.active" not in cache

        def _product_record(product: Product, **kwargs) -> ProductListRecord:
            return ProductListRecord(
                id=product.id,
                name=product.name,
                slug=product.slug,
                status=product.status_display,
                unit=product.unit_display,
                supplier=ProductSupplierRecord(
                    id=product.supplier_id,
                    name=product.supplier.name,
                    origin_country=product.supplier.country_name,
                    origin_country_flag=product.supplier.unicode_flag,
                ),
                thumbnail=product.thumbnail.url if product.thumbnail else None,
                display_price=product.display_price,
                from_price=product.from_price,
                materials=product.materials_display,
                rooms=product.rooms_display,
                colors=[
                    ProductColorRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product.colors.all()
                ],
                shapes=[
                    ProductShapeRecord(
                        id=shape.id, name=shape.name, image=shape.image.url
                    )
                    for shape in product.shapes.all()
                ],
                variants=[
                    VariantDetailRecord(
                        id=option.variant.id,
                        name=option.variant.name,
                        image=option.variant.image.url
                        if option.variant.image
                        else None,
                        thumbnail=option.variant.thumbnail.url
                        if option.variant.thumbnail
                        else None,
                        is_standard=option.variant.is_standard,
                    )
                    for option in product.options.available()
                    if option.variant
                ],
                **kwargs,
            )

        with django_assert_max_num_queries(11):
            discount_active_list_from_cache()

        # After first hit, instances should have been added to cache.
        assert "discounts.active" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            discount_active_list_from_cache()

        # Assert that output is expected.
        assert len(cache.get("discounts.active")) == 3
        assert expired_discount_1 not in cache.get("discounts.active")
        assert cache.get("discounts.active") == [
            DiscountRecord(
                id=active_discount_1.id,
                name=active_discount_1.name,
                description=active_discount_1.description,
                slug=active_discount_1.slug,
                products=[
                    _product_record(
                        product=product_4,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                    _product_record(
                        product=product_2_option_1.product,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                    _product_record(
                        product=product_1,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("160.00"),
                            discounted_gross_percentage=Decimal("0.20"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    ),
                ],
                minimum_quantity=active_discount_1.minimum_quantity,
                maximum_quantity=active_discount_1.maximum_quantity,
                discount_gross_price=active_discount_1.discount_gross_price,
                discount_gross_percentage=active_discount_1.discount_gross_percentage,
                maximum_sold_quantity=active_discount_1.maximum_sold_quantity,
                total_sold_quantity=active_discount_1.total_sold_quantity,
                display_maximum_quantity=active_discount_1.display_maximum_quantity,
                active_at=active_discount_1.active_at,
                active_to=active_discount_1.active_to,
                ordering=active_discount_1.ordering,
            ),
            DiscountRecord(
                id=active_discount_2.id,
                name=active_discount_2.name,
                description=active_discount_2.description,
                slug=active_discount_2.slug,
                products=[
                    _product_record(
                        product=product_3,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("120.00"),
                            discounted_gross_percentage=Decimal("0.40"),
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    )
                ],
                minimum_quantity=active_discount_2.minimum_quantity,
                maximum_quantity=active_discount_2.maximum_quantity,
                discount_gross_price=active_discount_2.discount_gross_price,
                discount_gross_percentage=active_discount_2.discount_gross_percentage,
                maximum_sold_quantity=active_discount_2.maximum_sold_quantity,
                total_sold_quantity=active_discount_2.total_sold_quantity,
                display_maximum_quantity=active_discount_2.display_maximum_quantity,
                active_at=active_discount_2.active_at,
                active_to=active_discount_2.active_to,
                ordering=active_discount_2.ordering,
            ),
            DiscountRecord(
                id=active_discount_3.id,
                name=active_discount_3.name,
                description=active_discount_3.description,
                slug=active_discount_3.slug,
                products=[
                    _product_record(
                        product=product_2,
                        discount=ProductDiscountRecord(
                            is_discounted=True,
                            discounted_gross_price=Decimal("200.00"),
                            discounted_gross_percentage=None,
                            maximum_sold_quantity=None,
                            remaining_quantity=None,
                        ),
                    )
                ],
                minimum_quantity=active_discount_3.minimum_quantity,
                maximum_quantity=active_discount_3.maximum_quantity,
                discount_gross_price=active_discount_3.discount_gross_price,
                discount_gross_percentage=active_discount_3.discount_gross_percentage,
                maximum_sold_quantity=active_discount_3.maximum_sold_quantity,
                total_sold_quantity=active_discount_3.total_sold_quantity,
                display_maximum_quantity=active_discount_3.display_maximum_quantity,
                active_at=active_discount_3.active_at,
                active_to=active_discount_3.active_to,
                ordering=active_discount_3.ordering,
            ),
        ]
