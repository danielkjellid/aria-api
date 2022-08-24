from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

import pytest

from aria.categories.tests.utils import create_category
from aria.discounts.tests.utils import create_discount
from aria.products.models import Product, ProductOption
from aria.products.records import (
    ProductColorRecord,
    ProductListRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.selectors import (
    _product_calculate_discounted_price,
    product_calculate_discounted_price_for_option,
    product_calculate_discounted_price_for_product,
    product_detail,
    product_get_discount_for_option,
    product_get_discount_for_product,
    product_get_price_from_options,
    product_list_by_category,
    product_list_by_category_from_cache,
    product_list_for_sale_for_qs,
    product_list_record,
    product_options_list_for_product,
)
from aria.products.tests.utils import create_product, create_product_option

pytestmark = pytest.mark.django_db


class TestProductsSelectors:

    ###########################
    # Records selectors tests #
    ###########################

    def test_selector_product_list_record(self, django_assert_max_num_queries):
        """
        Make sure the product_list_record selector enforeces the usage
        of prefetched values and that it does not cause any queries.
        """

        create_product(product_name="Product 1")
        create_product(product_name="Product 2")
        create_product(product_name="Product 3")

        products = Product.objects.all()

        assert len(products) == 3

        with django_assert_max_num_queries(0):
            with pytest.raises(AssertionError):
                product_list_record(products[0])
                product_list_record(products[1])
                product_list_record(products[2])

        products = products.preload_for_list()

        assert len(products) == 3

        with django_assert_max_num_queries(0):
            product_list_record(products[0])
            product_list_record(products[1])
            product_list_record(products[2])

    ###########################
    # Options selectors tests #
    ###########################

    def test_selector_product_get_price_from_options(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_get_price_from_options selector returns
        the lowest product price based on options within query limits.
        """

        product = create_product()

        create_product_option(product=product, gross_price=Decimal("100.00"))
        create_product_option(product=product, gross_price=Decimal("200.00"))
        create_product_option(product=product, gross_price=Decimal("300.00"))
        create_product_option(product=product, gross_price=Decimal("400.00"))

        # Uses 1 query to aggregate price.
        with django_assert_max_num_queries(1):
            lowest_price = product_get_price_from_options(product=product)

        assert lowest_price == Decimal("100.00")

        product_with_annotation = (
            Product.objects.filter(id=product.id).annotate_from_price().first()
        )

        # Product with annotated value should not hit db.
        with django_assert_max_num_queries(0):
            lowest_annotated_price = product_get_price_from_options(
                product=product_with_annotation
            )

        assert lowest_annotated_price == Decimal("100.00")

    def test_selector_product_options_list_for_product(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_options_list_for_product selector returns
        as expected, both with and without a prefetch.
        """

        product_1 = create_product(product_name="Test Product 1", options=[])
        create_product_option(product=product_1)
        create_product_option(product=product_1, gross_price=Decimal(300.00))
        create_product_option(product=product_1, gross_price=Decimal(400.00))

        # First test without prefetched attribute.
        # Uses 1 query for getting options + sizes and 1 for prefetching
        # active discounts.
        with django_assert_max_num_queries(2):
            options = product_options_list_for_product(product=product_1)

        assert len(options) == 3

        prefetched_product = (
            Product.objects.filter(id=product_1.id)
            .with_available_options_and_option_discounts()
            .first()
        )

        # Test with prefetched attribute.
        # Uses 0 queries if the arg sent in is already prefetched.
        with django_assert_max_num_queries(0):
            options = product_options_list_for_product(product=prefetched_product)

        assert len(options) == 3

    #####################################
    # Product discounts selectors tests #
    #####################################

    def test_selector__product_calculate_discounted_price(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the _product_calculate_discounted_price selector calculates and
        returns correct value within query limits.
        """

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.20"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("200.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = _product_calculate_discounted_price(
                price=Decimal("100.00"), discount=percentage_discount
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = _product_calculate_discounted_price(
                price=Decimal("400.00"), discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("80.00")
        assert discounted_fixed_price == Decimal("200.00")

    def test_selector_product_calculate_discounted_price_for_product(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_calculate_discounted_price_for_product selector
        calculates and returns correct value within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1, gross_price=Decimal("100.00"))
        product_1 = Product.objects.filter(id=product_1.id).preload_for_list().first()

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        product_2 = create_product(product_name="Product 2")
        create_product_option(product=product_2, gross_price=Decimal("500.00"))
        product_2 = Product.objects.filter(id=product_2.id).preload_for_list().first()

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("200.00"),
            products=[product_2],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = (
                product_calculate_discounted_price_for_product(
                    product=product_1, discount=percentage_discount
                )
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = product_calculate_discounted_price_for_product(
                product=product_2, discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("80.00")
        assert discounted_fixed_price == Decimal("200.00")

    def test_selector_product_calculate_discounted_price_for_option(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_calculate_discounted_price_for_option selector
        calculates and returns correct value within query limits.
        """

        option_1 = create_product_option(
            product=create_product(product_name="Product 1"),
            gross_price=Decimal("100.00"),
        )
        option_2 = create_product_option(
            product=create_product(product_name="Product 2"),
            gross_price=Decimal("500.00"),
        )

        percentage_discount = create_discount(
            discount_gross_percentage=Decimal("0.30"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        fixed_price_discount = create_discount(
            discount_gross_price=Decimal("100.00"),
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        with django_assert_max_num_queries(0):
            discounted_percentage_price = product_calculate_discounted_price_for_option(
                option=option_1, discount=percentage_discount
            )

        with django_assert_max_num_queries(0):
            discounted_fixed_price = product_calculate_discounted_price_for_option(
                option=option_2, discount=fixed_price_discount
            )

        assert discounted_percentage_price == Decimal("70.00")
        assert discounted_fixed_price == Decimal("100.00")

    def test_selector_product_get_discount_for_product(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_get_discount_for_product returns expected
        output within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        create_product_option(product=product_1, gross_price=Decimal("200.00"))
        create_product_option(product=product_1, gross_price=Decimal("300.00"))
        create_product_option(product=product_1, gross_price=Decimal("400.00"))
        create_product_option(product=product_1, gross_price=Decimal("500.00"))

        product_2 = create_product(product_name="Product 2")
        option_2 = create_product_option(
            product=product_2, gross_price=Decimal("100.00")
        )

        product_3 = create_product(product_name="Product 3")
        create_product_option(product=product_3, gross_price=Decimal("200.00"))

        create_discount(
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            product_options=[option_2],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_1_discount = product_get_discount_for_product(product=product_1)

        assert product_1_discount is not None
        assert product_1_discount.is_discounted is True
        assert product_1_discount.discounted_gross_price == Decimal("160.00")

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_2_discount = product_get_discount_for_product(product=product_2)

        assert product_2_discount is not None
        assert product_2_discount.is_discounted is True
        assert product_2_discount.discounted_gross_price == Decimal("80.00")

        # Uses 4 queries:
        # - 1x for getting product options in fallback
        # - 1x for prefetching options discounts
        # - 1x for getting product discounts in fallback
        # - 1x for calculating lowest option price
        with django_assert_max_num_queries(4):
            product_3_discount = product_get_discount_for_product(product=product_3)

        assert product_3_discount is None

        products_prefetched = (
            Product.objects.all()
            .with_active_product_discounts()
            .with_active_options_discounts()
            .annotate_from_price()
            .order_by("created_at")
        )

        assert len(products_prefetched) == 3

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_1_discount = product_get_discount_for_product(
                product=products_prefetched[0]
            )

        assert prefetched_product_1_discount is not None
        assert prefetched_product_1_discount.is_discounted is True
        assert prefetched_product_1_discount.discounted_gross_price == Decimal("160.00")

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_2_discount = product_get_discount_for_product(
                product=products_prefetched[1]
            )

        assert prefetched_product_2_discount is not None
        assert prefetched_product_2_discount.is_discounted is True
        assert prefetched_product_2_discount.discounted_gross_price == Decimal("80.00")

        # Should only use prefetched attributes, and should not hit db.
        with django_assert_max_num_queries(0):
            prefetched_product_3_discount = product_get_discount_for_product(
                product=products_prefetched[2]
            )

        assert prefetched_product_3_discount is None

    def test_selector_product_get_discount_for_option(  # pylint: disable=too-many-locals, too-many-statements
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that the product_get_discount_for_option returns expected
        output within query limits.
        """

        product_1 = create_product(product_name="Product 1")
        option_1 = create_product_option(
            product=product_1, gross_price=Decimal("100.00")
        )
        option_2 = create_product_option(
            product=product_1, gross_price=Decimal("200.00")
        )
        option_3 = create_product_option(
            product=product_1, gross_price=Decimal("300.00")
        )

        product_2 = create_product(product_name="Product 2")
        option_4 = create_product_option(
            product=product_2, gross_price=Decimal("400.00")
        )
        option_5 = create_product_option(
            product=product_2, gross_price=Decimal("200.00")
        )

        create_discount(
            name="Fixed 100",
            discount_gross_price=Decimal("100.00"),
            product_options=[option_3],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        create_discount(
            name="20% off",
            discount_gross_percentage=Decimal("0.20"),
            products=[product_1],
            product_options=[option_4],
            active_at=timezone.now(),
            active_to=timezone.now() + timedelta(minutes=10),
        )

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_1_discount = product_get_discount_for_option(product_option=option_1)

        assert option_1_discount is not None
        assert option_1_discount.is_discounted is True
        assert option_1_discount.discounted_gross_price == Decimal("80.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_2_discount = product_get_discount_for_option(product_option=option_2)

        assert option_2_discount is not None
        assert option_2_discount.is_discounted is True
        assert option_2_discount.discounted_gross_price == Decimal("160.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_3_discount = product_get_discount_for_option(product_option=option_3)

        assert option_3_discount is not None
        assert option_3_discount.is_discounted is True
        # option_3 has a more specific discount active than on the product level,
        # therefore that should be used.
        assert option_3_discount.discounted_gross_price == Decimal("100.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_4_discount = product_get_discount_for_option(product_option=option_4)

        assert option_4_discount is not None
        assert option_4_discount.is_discounted is True
        assert option_4_discount.discounted_gross_price == Decimal("320.00")

        # Uses 3 queries:
        # - 1x for getting discounts for option
        # - 1x for getting discounts for product
        # - 1x for calculating discount price
        with django_assert_max_num_queries(3):
            option_5_discount = product_get_discount_for_option(product_option=option_5)

        assert option_5_discount is None

        prefetched_products = list(
            Product.objects.all()
            .with_available_options_and_option_discounts()
            .with_active_product_discounts()
            .order_by("created_at")
        )

        def _get_prefetched_option(
            product: Product, option: ProductOption
        ) -> ProductOption:
            product_index = prefetched_products.index(product)
            return [
                o
                for o in prefetched_products[product_index].available_options
                if o.id == option.id
            ][0]

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_1_prefetched_discount = product_get_discount_for_option(
                product_option=_get_prefetched_option(product_1, option_1)
            )

        assert option_1_prefetched_discount is not None
        assert option_1_prefetched_discount.is_discounted is True
        assert option_1_prefetched_discount.discounted_gross_price == Decimal("80.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_2_prefetched_discount = product_get_discount_for_option(
                product_option=_get_prefetched_option(product_1, option_2)
            )

        assert option_2_prefetched_discount is not None
        assert option_2_prefetched_discount.is_discounted is True
        assert option_2_prefetched_discount.discounted_gross_price == Decimal("160.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_3_prefetched_discount = product_get_discount_for_option(
                product_option=_get_prefetched_option(product_1, option_3)
            )

        assert option_3_prefetched_discount is not None
        assert option_3_prefetched_discount.is_discounted is True
        # option_3 has a more specific discount active than on the product level,
        # therefore that should be used.
        assert option_3_prefetched_discount.discounted_gross_price == Decimal("100.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_4_prefetched_discount = product_get_discount_for_option(
                product_option=_get_prefetched_option(product_2, option_4)
            )

        assert option_4_prefetched_discount is not None
        assert option_4_prefetched_discount.is_discounted is True
        assert option_4_prefetched_discount.discounted_gross_price == Decimal("320.00")

        # Should use prefetched attributes, and not hit db.
        with django_assert_max_num_queries(0):
            option_5_prefetched_discount = product_get_discount_for_option(
                product_option=_get_prefetched_option(product_2, option_5)
            )

        assert option_5_prefetched_discount is None

    ###########################
    # Product selectors tests #
    ###########################

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
        # - 1x for prefetching shapes
        # - 1x for prefetching files
        # - 1x for prefetching options
        # - 1x for prefetching options discounts
        # - 1x for prefetching product discounts
        # - 1x for filtering categories
        # - 1x for selecting related supplier
        # - 1x for prefetching images
        with django_assert_max_num_queries(12):
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

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            products_by_subcat_1 = product_list_for_sale_for_qs(
                products=products_by_category_subcat_1, filters=None
            )

        print(products_by_subcat_1)
        print(list(reversed(products_subcat_1)))

        assert len(products_by_subcat_1) == 20
        # Qs is ordered by -created_at, so reverse list returned på util.
        assert products_by_subcat_1[0].id == list(reversed(products_subcat_1))[0].id
        assert products_by_subcat_1[19].id == list(reversed(products_subcat_1))[19].id

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

        # Uses 7 queries:
        # - 1 for getting products,
        # - 1 for preloading categories,
        # - 1 for preloading colors,
        # - 1 for preloading shapes,
        # - 1 for preloading images,
        # - 1 for preloading options,
        # - 1 for preloading files
        with django_assert_max_num_queries(7):
            filtered_products_by_subcat_2 = product_list_for_sale_for_qs(
                products=products_by_category_subcat_2, filters={"search": "awesome"}
            )

        # Assert that only awesome product is returned.
        assert len(filtered_products_by_subcat_2) == 1
        assert filtered_products_by_subcat_2[0].id == products_subcat_2[0].id

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
        assert (
            filtered_products_subcat_1[0].id == list(reversed(products_subcat_1))[0].id
        )
        assert (
            filtered_products_subcat_1[19].id
            == list(reversed(products_subcat_1))[19].id
        )

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
                from_price=Decimal("200.00"),
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
                from_price=Decimal("200.00"),
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
                from_price=Decimal("200.00"),
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
