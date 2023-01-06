from decimal import Decimal

from django.core.cache import cache

import pytest

from aria.categories.tests.utils import create_category
from aria.product_attributes.records import (
    ColorDetailRecord,
    MaterialDetailRecord,
    RoomDetailRecord,
    ShapeDetailRecord,
    VariantDetailRecord,
)
from aria.products.enums import ProductStatus
from aria.products.models import Product
from aria.products.records import ProductListRecord, ProductSupplierRecord
from aria.products.selectors.core import (
    product_detail,
    product_list_by_category,
    product_list_by_category_from_cache,
    product_list_for_sale,
    product_list_for_sale_for_qs,
    product_list_for_sale_from_cache,
)
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductCoreSelectors:
    def test_selector_product_detail(self, django_assert_max_num_queries) -> None:
        """
        Test that the product_detail selector works as expected and does
        not use an obscene amount of queries. It's a big boy.
        """

        product = create_product()
        create_product_option(product=product)
        create_product_option(product=product, gross_price=Decimal(300.00))

        # Uses 12 queries:
        # - 1x for getting product
        # - 1x for prefetching category children
        # - 1x for prefetching categories
        # - 1x for prefetching colors
        # - 1x for prefetching materials
        # - 1x for prefetching rooms
        # - 1x for prefetching shapes
        # - 1x for prefetching files
        # - 1x for prefetching options
        # - 1x for prefetching options discounts
        # - 1x for prefetching product discounts
        # - 1x for filtering categories
        # - 1x for selecting related supplier
        # - 1x for prefetching images
        with django_assert_max_num_queries(14):
            fetched_product = product_detail(product_id=product.id)

        assert fetched_product.id == product.id
        assert len(fetched_product.options) == len(product.options.all())
        assert len(fetched_product.categories) == len(product.categories.all())
        assert len(fetched_product.images) == len(product.images.all())
        assert len(fetched_product.shapes) == len(product.shapes.all())
        assert len(fetched_product.colors) == len(product.colors.all())

    def test_selector_product_list_for_sale_for_qs(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_list_for_qs selector returns expected response
        within query limit.
        """

        cat_1 = create_category(name="Main cat 1")
        subcat_1 = create_category(name="Sub cat 1", parent=cat_1)
        subcat_2 = create_category(name="Sub cat 2", parent=cat_1)

        products_subcat_1 = create_product(quantity=20)
        products_subcat_2 = create_product(quantity=15)

        for product in products_subcat_1:
            product.categories.set([subcat_1])

        for product in products_subcat_2:
            product.categories.set([subcat_2])

        products_by_category_subcat_1 = Product.objects.by_category(subcat_1)

        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading materials,
        # - 1 for preloading rooms
        # - 1 for preloading shapes,
        # - 1 for preloading options,
        # - 1 for preloading discounts
        # - 1 for preloading option prices
        # - 1 for preloading option discounts
        with django_assert_max_num_queries(9):
            products_by_subcat_1 = product_list_for_sale_for_qs(
                products=products_by_category_subcat_1, filters=None
            )

        assert len(products_by_subcat_1) == 20
        # Qs is ordered by -created_at, so reverse list returned på util.
        assert products_by_subcat_1[0].id == list(reversed(products_subcat_1))[0].id
        assert products_by_subcat_1[19].id == list(reversed(products_subcat_1))[19].id

        products_by_category_subcat_2 = Product.objects.by_category(subcat_2)

        with django_assert_max_num_queries(9):
            products_by_subcat_2 = product_list_for_sale_for_qs(
                products=products_by_category_subcat_2, filters=None
            )

        # Assert that only the products_subcat_2 is returned.
        assert len(products_by_subcat_2) == 15
        assert products_by_subcat_2[0].id == list(reversed(products_subcat_2))[0].id
        assert products_by_subcat_2[14].id == list(reversed(products_subcat_2))[14].id

        # Explicitly set name of first instance.
        products_subcat_2[0].name = "Awesome product"
        products_subcat_2[0].save()

        with django_assert_max_num_queries(9):
            filtered_products_by_subcat_2 = product_list_for_sale_for_qs(
                products=products_by_category_subcat_2, filters={"search": "awesome"}
            )

        # Assert that only awesome product is returned.
        assert len(filtered_products_by_subcat_2) == 1
        assert filtered_products_by_subcat_2[0].id == products_subcat_2[0].id

    def test_selector_product_list_for_sale(self, django_assert_max_num_queries):
        """
        Test that the product_list_for_sale selector returns expected output within
        query limits.
        """

        products = create_product(quantity=10, status=ProductStatus.AVAILABLE)
        create_product(quantity=5, status=ProductStatus.DRAFT)

        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading options,
        # - 1 for preloading discounts for options
        with django_assert_max_num_queries(9):
            available_products = product_list_for_sale(filters=None)

        # Assert that only available products are returned.
        assert len(available_products) == 10
        assert available_products[0].id == list(reversed(products))[0].id
        assert available_products[9].id == list(reversed(products))[9].id

        products[0].name = "Awesome product"
        products[0].save()

        with django_assert_max_num_queries(9):
            filtered_available_products = product_list_for_sale(
                filters={"search": "awesome"}
            )

        assert len(filtered_available_products) == 1
        assert filtered_available_products[0].id == products[0].id

    def test_selector_product_list_for_sale_from_cache(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_list_for_sale_from_cache selector returns correctly from
        cache, and output is expected within query limits.
        """

        products = create_product(quantity=10, status=ProductStatus.AVAILABLE)
        create_product(quantity=5, status=ProductStatus.DRAFT)

        cache.delete(f"products.for_sale.filters={None}")
        assert f"products.for_sale.filters={None}" not in cache

        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading options variants,
        # - 1 for preloading discounts
        # - 1 for preloading options,
        # - 1 for preloading discounts for options
        with django_assert_max_num_queries(9):
            product_list_for_sale_from_cache(filters=None)

        # After first hit, instance should have been added to cache.
        assert f"products.for_sale.filters={None}" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            product_list_for_sale_from_cache(filters=None)

        assert len(cache.get(f"products.for_sale.filters={None}")) == 10
        assert (
            cache.get(f"products.for_sale.filters={None}")[0].id
            == list(reversed(products))[0].id
        )
        assert (
            cache.get(f"products.for_sale.filters={None}")[9].id
            == list(reversed(products))[9].id
        )

        products[0].name = "Awesome product"
        products[0].save()

        # Adding search filters should re-hit db.
        with django_assert_max_num_queries(9):
            product_list_for_sale_from_cache(filters={"search": "awesome"})

        # New key with appended filters should have been added to cache.
        assert "products.for_sale.filters={'search': 'awesome'}" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(9):
            product_list_for_sale_from_cache(filters={"search": "awesome"})

        assert len(cache.get("products.for_sale.filters={'search': 'awesome'}")) == 1
        assert (
            cache.get("products.for_sale.filters={'search': 'awesome'}")[0].id
            == products[0].id
        )

    def test_selector_product_list_by_category(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test the product_list_by_category selector returns expected response within
        query limit for a specific category.
        """

        cat_1 = create_category(name="Main cat 1")
        subcat_1 = create_category(name="Sub cat 1", parent=cat_1)
        subcat_2 = create_category(name="Sub cat 2", parent=cat_1)

        products_subcat_1 = create_product(quantity=20)
        products_subcat_2 = create_product(quantity=15)

        for product in products_subcat_1:
            product.categories.set([subcat_1])

        for product in products_subcat_2:
            product.categories.set([subcat_2])

        # First test getting products based on category subcat_1.
        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(9):
            filtered_products_subcat_1 = product_list_by_category(
                category=subcat_1, filters=None
            )

        # Assert that only the products_subcat_1 is returned.
        assert len(filtered_products_subcat_1) == 20
        assert (
            filtered_products_subcat_1[0].id == list(reversed(products_subcat_1))[0].id
        )
        assert (
            filtered_products_subcat_1[19].id
            == list(reversed(products_subcat_1))[19].id
        )

        # Then test getting products based on category subcat_2.
        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(9):
            filtered_products_subcat_2 = product_list_by_category(
                category=subcat_2, filters=None
            )

        # Assert that only the products_subcat_2 is returned.
        assert len(filtered_products_subcat_2) == 15
        assert (
            filtered_products_subcat_2[0].id == list(reversed(products_subcat_2))[0].id
        )
        assert (
            filtered_products_subcat_2[14].id
            == list(reversed(products_subcat_2))[14].id
        )

        # Explicitly set name of first instance.
        products_subcat_2[0].name = "Awesome product"
        products_subcat_2[0].save()

        # Test searching on already filtered list.
        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(9):
            products_subcat_2_search = product_list_by_category(
                category=subcat_2, filters={"search": "awesome"}
            )

        # Assert that only awesome product is returned.
        assert len(products_subcat_2_search) == 1
        assert products_subcat_2_search[0].id == products_subcat_2[0].id

    def test_selector_product_list_by_category_from_cache(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_list_by_category_from_cache correctly returns from
        cache, and output is as expected, within query limits.
        """

        cat = create_category(name="Main cat 1")
        subcat = create_category(name="Sub cat 1", parent=cat)

        product_1 = create_product(product_name="Awesome product")
        product_2 = create_product(product_name="Product 2")

        for product in [product_1, product_2]:
            product.categories.set([subcat])

        cache.delete(f"products.category_id={subcat.id}.filters={None}")
        assert f"products.category_id={subcat.id}.filters={None}" not in cache

        # Uses 9 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading materials
        # - 1 for preloading rooms
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(9):
            product_list_by_category_from_cache(category=subcat, filters=None)

        # After first hit, instance should have been added to cache.
        assert f"products.category_id={subcat.id}.filters={None}" in cache

        # Should be cached, and no queries should hit db.
        with django_assert_max_num_queries(0):
            product_list_by_category_from_cache(category=subcat, filters=None)

        # Assert that output is expected.
        assert len(cache.get(f"products.category_id={subcat.id}.filters={None}")) == 2
        assert cache.get(f"products.category_id={subcat.id}.filters={None}") == [
            ProductListRecord(
                id=product_2.id,
                name=product_2.name,
                slug=product_2.slug,
                status=product_2.status_display,
                unit=product_2.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_2.supplier.id,
                    name=product_2.supplier.name,
                    origin_country=product_2.supplier.country_name,
                    origin_country_flag=product_2.supplier.unicode_flag,
                ),
                from_price=Decimal("200.00"),
                display_price=True,
                materials=[
                    MaterialDetailRecord(id=material.id, name=material.name)
                    for material in product_2.materials.all()
                ],
                rooms=[
                    RoomDetailRecord(id=room.id, name=room.name)
                    for room in product_2.rooms.all()
                ],
                colors=[
                    ColorDetailRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_2.colors.all()
                ],
                shapes=[
                    ShapeDetailRecord(
                        id=shape.id, name=shape.name, image_url=shape.image.url
                    )
                    for shape in product_2.shapes.all()
                ],
                variants=[
                    VariantDetailRecord(
                        id=option.variant.id,
                        name=option.variant.name,
                        image_url=option.variant.image_url,
                        image80x80_url=option.variant.image80x80_url,
                        image380x575_url=option.variant.image380x575_url,
                        is_standard=option.variant.is_standard,
                    )
                    for option in product_2.options.all()
                    if option.variant
                ],
            ),
            ProductListRecord(
                id=product_1.id,
                name=product_1.name,
                slug=product_1.slug,
                status=product_1.status_display,
                unit=product_1.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_1.supplier.id,
                    name=product_1.supplier.name,
                    origin_country=product_1.supplier.country_name,
                    origin_country_flag=product_1.supplier.unicode_flag,
                ),
                from_price=Decimal("200.00"),
                display_price=True,
                materials=[
                    MaterialDetailRecord(id=material.id, name=material.name)
                    for material in product_1.materials.all()
                ],
                rooms=[
                    RoomDetailRecord(id=room.id, name=room.name)
                    for room in product_1.rooms.all()
                ],
                colors=[
                    ColorDetailRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_1.colors.all()
                ],
                shapes=[
                    ShapeDetailRecord(
                        id=shape.id, name=shape.name, image_url=shape.image.url
                    )
                    for shape in product_1.shapes.all()
                ],
                variants=[
                    VariantDetailRecord(
                        id=option.variant.id,
                        name=option.variant.name,
                        image_url=option.variant.image_url,
                        image80x80_url=option.variant.image80x80_url,
                        image380x575_url=option.variant.image380x575_url,
                        is_standard=option.variant.is_standard,
                    )
                    for option in product_1.options.all()
                    if option.variant
                ],
            ),
        ]

        # Adding search filters should re-hit db.
        with django_assert_max_num_queries(9):
            product_list_by_category_from_cache(
                category=subcat, filters={"search": "awesome"}
            )

        # New key with appended filters should have been added to cache.
        assert (
            f"products.category_id={subcat.id}.filters={{'search': 'awesome'}}" in cache
        )

        # Re-querying the same search filters should not hit db.
        with django_assert_max_num_queries(0):
            product_list_by_category_from_cache(
                category=subcat, filters={"search": "awesome"}
            )

        # Assert that only the filtered product is returned.
        assert (
            len(
                cache.get(
                    f"products.category_id={subcat.id}.filters={{'search': 'awesome'}}"
                )
            )
            == 1
        )
        assert cache.get(
            f"products.category_id={subcat.id}.filters={{'search': 'awesome'}}"
        ) == [
            ProductListRecord(
                id=product_1.id,
                name=product_1.name,
                slug=product_1.slug,
                status=product_1.status_display,
                unit=product_1.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_1.supplier.id,
                    name=product_1.supplier.name,
                    origin_country=product_1.supplier.country_name,
                    origin_country_flag=product_1.supplier.unicode_flag,
                ),
                from_price=Decimal("200.00"),
                display_price=True,
                materials=[
                    MaterialDetailRecord(id=material.id, name=material.name)
                    for material in product.materials.all()
                ],
                rooms=[
                    RoomDetailRecord(id=room.id, name=room.name)
                    for room in product_1.rooms.all()
                ],
                colors=[
                    ColorDetailRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_1.colors.all()
                ],
                shapes=[
                    ShapeDetailRecord(
                        id=shape.id, name=shape.name, image_url=shape.image.url
                    )
                    for shape in product_1.shapes.all()
                ],
                variants=[
                    VariantDetailRecord(
                        id=option.variant.id,
                        name=option.variant.name,
                        image_url=option.variant.image_url,
                        image80x80_url=option.variant.image80x80_url,
                        image380x575_url=option.variant.image380x575_url,
                        is_standard=option.variant.is_standard,
                    )
                    for option in product_1.options.all()
                    if option.variant
                ],
            ),
        ]
