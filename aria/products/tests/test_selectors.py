from decimal import Decimal

from django.core.cache import cache

import pytest

from aria.categories.tests.utils import create_category
from aria.products.models import Product
from aria.products.records import (
    ProductColorRecord,
    ProductListRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.selectors import (
    product_detail,
    product_list_by_category,
    product_list_by_category_from_cache,
    product_options_list_for_product,
    products_for_sale_list_for_qs,
)
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductsSelectors:
    def test_product_options_list_for_product(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_options_list_for_product selector returns
        as expected, both with and without a prefetch.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1)
        create_product_option(product=product_1, gross_price=Decimal(300.00))
        create_product_option(product=product_1, gross_price=Decimal(400.00))

        # First test without prefetched attribute.
        # Uses 1 query for getting options + sizes.
        with django_assert_max_num_queries(1):
            options = product_options_list_for_product(product=product_1)

        assert len(options) == 3

        # Prefetching here uses 2 queries, but we usually have to get
        # the product somehow anyways.
        prefetched_product = (
            Product.objects.filter(id=product_1.id).with_available_options().first()
        )

        # Test with prefetched attribute.
        # Uses 0 queries if the arg sent in is already prefetched.
        with django_assert_max_num_queries(0):
            options = product_options_list_for_product(product=prefetched_product)

        assert len(options) == 3

    def test_product_detail(self, django_assert_max_num_queries) -> None:
        """
        Test that the product_detail selector works as expected and does
        not use an obscene amount of queries. It's a big boy.
        """

        product = create_product()

        # Uses 12 queries: Uses 7 to get basic product details and relations,
        # 4 to get right amount og categories and 1 to get options.
        with django_assert_max_num_queries(12):
            fetched_product = product_detail(product_id=product.id)

        assert fetched_product.id == product.id
        assert len(fetched_product.options) == len(product.options.all())
        assert len(fetched_product.categories) == len(product.categories.all())
        assert len(fetched_product.images) == len(product.images.all())
        assert len(fetched_product.shapes) == len(product.shapes.all())
        assert len(fetched_product.colors) == len(product.colors.all())

    def test_products_for_sale_list_for_qs(self, django_assert_max_num_queries) -> None:
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

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            products_by_subcat_1 = products_for_salelist_for_qs(
                products=products_by_category_subcat_1, filters=None
            )

        assert len(products_by_subcat_1) == 20
        assert products_by_subcat_1[0].id == products_subcat_1[0].id
        assert products_by_subcat_1[19].id == products_subcat_1[19].id

        products_by_category_subcat_2 = Product.objects.by_category(subcat_2)

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            products_by_subcat_2 = products_for_sale_list_for_qs(
                products=products_by_category_subcat_2, filters=None
            )

        # Assert that only the products_subcat_2 is returned.
        assert len(products_by_subcat_2) == 15
        assert products_by_subcat_2[0].id == products_subcat_2[0].id
        assert products_by_subcat_2[14].id == products_subcat_2[14].id

        # Explicitly set name of first instance.
        products_subcat_2[0].name = "Awesome product"
        products_subcat_2[0].save()

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            filtered_products_by_subcat_2 = products_for_sale_list_for_qs(
                products=products_by_category_subcat_2, filters={"search": "awesome"}
            )

        # Assert that only awesome product is returned.
        assert len(filtered_products_by_subcat_2) == 1
        assert filtered_products_by_subcat_2[0].id == products_subcat_2[0].id

    def test_product_list_by_category(self, django_assert_max_num_queries) -> None:
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
        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            filtered_products_subcat_1 = product_list_by_category(
                category=subcat_1, filters=None
            )

        # Assert that only the products_subcat_1 is returned.
        assert len(filtered_products_subcat_1) == 20
        assert filtered_products_subcat_1[0].id == products_subcat_1[0].id
        assert filtered_products_subcat_1[19].id == products_subcat_1[19].id

        # Then test getting products based on category subcat_2.
        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            filtered_products_subcat_2 = product_list_by_category(
                category=subcat_2, filters=None
            )

        # Assert that only the products_subcat_2 is returned.
        assert len(filtered_products_subcat_2) == 15
        assert filtered_products_subcat_2[0].id == products_subcat_2[0].id
        assert filtered_products_subcat_2[14].id == products_subcat_2[14].id

        # Explicitly set name of first instance.
        products_subcat_2[0].name = "Awesome product"
        products_subcat_2[0].save()

        # Test searching on already filtered list.
        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            products_subcat_2_search = product_list_by_category(
                category=subcat_2, filters={"search": "awesome"}
            )

        # Assert that only awesome product is returned.
        assert len(products_subcat_2_search) == 1
        assert products_subcat_2_search[0].id == products_subcat_2[0].id

    def test_product_list_by_category_from_cache(
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

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
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
                id=product_1.id,
                name=product_1.name,
                slug=product_1.slug,
                unit=product_1.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_1.supplier.id,
                    name=product_1.supplier.name,
                    origin_country=product_1.supplier.origin_country.name,
                    origin_country_flag=product_1.supplier.origin_country.unicode_flag,
                ),
                from_price=0.0,
                display_price=True,
                materials=product_1.materials_display,
                rooms=product_1.rooms_display,
                colors=[
                    ProductColorRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_1.colors.all()
                ],
                shapes=[
                    ProductShapeRecord(
                        id=shape.id, name=shape.name, image=shape.image.url
                    )
                    for shape in product_1.shapes.all()
                ],
                variants=[
                    ProductVariantRecord(
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
                    for option in product_1.options.all()
                    if option.variant
                ],
            ),
            ProductListRecord(
                id=product_2.id,
                name=product_2.name,
                slug=product_2.slug,
                unit=product_2.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_2.supplier.id,
                    name=product_2.supplier.name,
                    origin_country=product_2.supplier.origin_country.name,
                    origin_country_flag=product_2.supplier.origin_country.unicode_flag,
                ),
                from_price=0.0,
                display_price=True,
                materials=product_2.materials_display,
                rooms=product_2.rooms_display,
                colors=[
                    ProductColorRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_2.colors.all()
                ],
                shapes=[
                    ProductShapeRecord(
                        id=shape.id, name=shape.name, image=shape.image.url
                    )
                    for shape in product_2.shapes.all()
                ],
                variants=[
                    ProductVariantRecord(
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
                    for option in product_2.options.all()
                    if option.variant
                ],
            ),
        ]

        # Adding search filters should re-hit db.
        with django_assert_max_num_queries(7):
            product_list_by_category_from_cache(
                category=subcat, filters={"search": "awesome"}
            )

        # New key with appended filters should have been added to cache.
        assert (
            f"products.category_id={subcat.id}.filters={{'search': 'awesome'}}" in cache
        )

        # Adding search filters should re-hit db.
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
                unit=product_1.unit_display,
                supplier=ProductSupplierRecord(
                    id=product_1.supplier.id,
                    name=product_1.supplier.name,
                    origin_country=product_1.supplier.origin_country.name,
                    origin_country_flag=product_1.supplier.origin_country.unicode_flag,
                ),
                from_price=0.0,
                display_price=True,
                materials=product_1.materials_display,
                rooms=product_1.rooms_display,
                colors=[
                    ProductColorRecord(
                        id=color.id, name=color.name, color_hex=color.color_hex
                    )
                    for color in product_1.colors.all()
                ],
                shapes=[
                    ProductShapeRecord(
                        id=shape.id, name=shape.name, image=shape.image.url
                    )
                    for shape in product_1.shapes.all()
                ],
                variants=[
                    ProductVariantRecord(
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
                    for option in product_1.options.all()
                    if option.variant
                ],
            ),
        ]
