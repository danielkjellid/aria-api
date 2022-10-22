import os
from decimal import Decimal
from unittest.mock import ANY

import pytest

from aria.categories.tests.utils import create_category
from aria.core.exceptions import ApplicationError
from aria.core.records import BaseArrayFieldLabelRecord
from aria.core.tests.utils import create_image_file
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product
from aria.products.records import ProductRecord, ProductSupplierRecord
from aria.products.services.core import product_create, product_update
from aria.products.tests.utils import create_color, create_product, create_shape
from aria.suppliers.tests.utils import get_or_create_supplier

pytestmark = pytest.mark.django_db


class TestProductsCoreServices:
    def test_service_product_create(self, django_assert_max_num_queries):
        """
        Test that the product_create service successfully creates a product within
        query limits, and rolls back transaction when exceptions are raised.
        """

        # Suppliers
        supplier = get_or_create_supplier()

        # Categories
        main_category = create_category(name="Main category")
        sub_category1 = create_category(name="Sub category 1", parent=main_category)
        sub_category2 = create_category(name="Sub category 2", parent=main_category)
        sub_category3 = create_category(name="Sub category 3", parent=main_category)

        category_ids = [sub_category1.id, sub_category2.id]

        # Shapes
        shape_square = create_shape(name="Square")
        shape_circular = create_shape(name="Circular")

        shape_ids = [shape_square.id, shape_circular.id]

        # Colors
        color_white = create_color(name="White", color_hex="#FFFFFF")
        color_gray = create_color(name="Red", color_hex="#CCCCCC")

        color_ids = [color_white.id, color_gray.id]

        # Thumbnail
        thumbnail = create_image_file(
            name="thumbnail", extension="jpeg", width=380, height=575
        )

        current_products_in_db_count = Product.objects.count()

        assert current_products_in_db_count == 0

        expected_output = ProductRecord.construct(
            id=ANY,
            name="New product",
            supplier=ProductSupplierRecord(
                id=supplier.id,
                name=supplier.name,
                origin_country=supplier.country_name,
                origin_country_flag=supplier.unicode_flag,
            ),
            slug="new-product",
            status=ProductStatus.AVAILABLE.label,
            search_keywords="keyword1 keyword2",
            description="A completely new product",
            unit=ProductUnit.PCS.label,
            vat_rate=Decimal("0.25"),
            available_in_special_sizes=False,
            absorption=None,
            is_imported_from_external_source=False,
            materials=[
                BaseArrayFieldLabelRecord(name="Kompositt"),
                BaseArrayFieldLabelRecord(name="Metall"),
            ],
            rooms=[BaseArrayFieldLabelRecord(name="Bad")],
            thumbnail=ANY,
        )

        # Passing in a main category should raise application error.
        with django_assert_max_num_queries(7):
            with pytest.raises(ApplicationError):
                product_create(
                    name="New product",
                    slug="new-product",
                    supplier=supplier,
                    status=ProductStatus.AVAILABLE,
                    description="A completely new product",
                    unit=ProductUnit.PCS,
                    category_ids=[main_category.id],
                    thumbnail=thumbnail,
                )

        # Passing in a thumbnail far too large should raise application error.
        with django_assert_max_num_queries(3):
            with pytest.raises(ApplicationError):
                product_create(
                    name="New product",
                    slug="new-product",
                    supplier=supplier,
                    status=ProductStatus.AVAILABLE,
                    description="A completely new product",
                    unit=ProductUnit.PCS,
                    thumbnail=create_image_file(
                        name="should-fail", extension="JPEG", width=1000, height=2000
                    ),
                )

        with django_assert_max_num_queries(16):
            created_product = product_create(
                name="New product",
                slug="new-product",
                supplier=supplier,
                status=ProductStatus.AVAILABLE,
                search_keywords="keyword1 keyword2",
                description="A completely new product",
                unit=ProductUnit.PCS,
                category_ids=category_ids,
                shape_ids=shape_ids,
                color_ids=color_ids,
                vat_rate=Decimal("0.25"),
                materials=[  # Wood does not exist, and should be skipped.
                    "kompositt",
                    "metall",
                    "wood",
                ],
                rooms=["badrom"],
                absorption=None,
                display_price=True,
                can_be_purchased_online=True,
                can_be_picked_up=False,
                thumbnail=thumbnail,
            )

        db_product = Product.objects.get(id=created_product.id)

        assert Product.objects.count() == current_products_in_db_count + 1
        assert created_product == expected_output
        assert sub_category3 not in list(db_product.categories.all())
        assert list(db_product.categories.all()) == [sub_category1, sub_category2]
        assert list(db_product.shapes.all()) == [shape_square, shape_circular]
        assert list(db_product.colors.all()) == [color_white, color_gray]

    def test_service_product_update(self, django_assert_max_num_queries):
        """
        Test that the product_update service successfully updates a product within
        query limits, and rolls back transaction when exceptions are raised.
        """

        supplier = get_or_create_supplier()

        # Categories
        main_category = create_category(name="Main category")
        sub_category1 = create_category(name="Sub category 1", parent=main_category)
        sub_category2 = create_category(name="Sub category 2", parent=main_category)

        # Shapes
        shape_square = create_shape(name="Square")
        shape_circular = create_shape(name="Circular")

        # Colors
        color_white = create_color(name="White", color_hex="#FFFFFF")
        color_gray = create_color(name="Red", color_hex="#CCCCCC")

        product = create_product(
            supplier=supplier,
            product_name="New product",
            search_keywords="keyword1",
            description="A completely new product",
            status=ProductStatus.AVAILABLE,
            available_in_special_sizes=False,
        )

        product.categories.set([sub_category1])
        product.shapes.set([shape_square])
        product.colors.set([color_white])

        product.rooms = ["badrom"]
        product.materials = [
            "kompositt",
        ]

        product.thumbnail = create_image_file(
            name="thumbnail", extension="jpeg", width=380, height=575
        )
        old_thumbnail_expected_name = (
            "media/products/example-supplier/new-product-0/images/thumbnail.jpeg"
        )
        old_thumbnail_path = product.thumbnail.path

        product.save()

        old_product_instance = product

        current_products_in_db_count = Product.objects.count()

        assert current_products_in_db_count == 1
        assert list(product.categories.all()) == [sub_category1]
        assert list(product.shapes.all()) == [shape_square]
        assert list(product.colors.all()) == [color_white]
        assert product.thumbnail.name == old_thumbnail_expected_name

        expected_output = ProductRecord.construct(
            id=ANY,
            name="New product 0",
            supplier=ProductSupplierRecord(
                id=supplier.id,
                name=supplier.name,
                origin_country=supplier.country_name,
                origin_country_flag=supplier.unicode_flag,
            ),
            slug="new-product",
            status=ProductStatus.HIDDEN.label,
            search_keywords="keyword1 keyword2",
            description="The same product, but edited!",
            unit=ProductUnit.PCS.label,
            vat_rate=Decimal("0.25"),
            available_in_special_sizes=False,
            absorption=None,
            is_imported_from_external_source=False,
            materials=[
                BaseArrayFieldLabelRecord(name="Kompositt"),
                BaseArrayFieldLabelRecord(name="Metall"),
            ],
            rooms=[
                BaseArrayFieldLabelRecord(name="Bad"),
                BaseArrayFieldLabelRecord(name="Uterom"),
            ],
            thumbnail=ANY,
        )

        # Passing in a main category should raise application error.
        with django_assert_max_num_queries(9):
            with pytest.raises(ApplicationError):
                product_update(product=product, category_ids=[main_category.id])

        # Passing in a thumbnail far too large should raise application error.
        with django_assert_max_num_queries(3):
            with pytest.raises(ApplicationError):
                product_update(
                    product=product,
                    thumbnail=create_image_file(
                        name="should-fail", extension="JPEG", width=1000, height=2000
                    ),
                )

        # No changes, should only create savepoints.
        with django_assert_max_num_queries(2):
            product_update(product=product)

        with django_assert_max_num_queries(20):
            updated_product = product_update(
                product=product,
                category_ids=[sub_category1.id, sub_category2.id],
                shape_ids=[shape_square.id, shape_circular.id],
                color_ids=[color_white.id, color_gray.id],
                materials=[
                    "kompositt",
                    "metall",
                    "wood",  # Wood does not exist, and should be skipped.
                ],
                rooms=["badrom", "uterom"],
                status=ProductStatus.HIDDEN,
                search_keywords="keyword1 keyword2",
                description="The same product, but edited!",
                thumbnail=create_image_file(
                    name="new-thumbnail", extension="jpeg", width=380, height=575
                ),
            )

        db_product = Product.objects.get(id=updated_product.id)

        assert Product.objects.count() == current_products_in_db_count
        assert updated_product.id == old_product_instance.id
        assert updated_product == expected_output
        assert list(db_product.categories.all()) == [sub_category1, sub_category2]
        assert list(db_product.shapes.all()) == [shape_square, shape_circular]
        assert list(db_product.colors.all()) == [color_white, color_gray]
        assert db_product.status == ProductStatus.HIDDEN
        assert db_product.search_keywords == "keyword1 keyword2"
        assert db_product.description == "The same product, but edited!"
        assert (
            db_product.thumbnail.name
            == "media/products/example-supplier/new-product-0/images/new-thumbnail.jpeg"
        )
        assert os.path.exists(db_product.thumbnail.path) is True
        assert os.path.exists(old_thumbnail_path) is False