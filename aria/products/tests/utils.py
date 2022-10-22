import tempfile
from decimal import Decimal
from typing import Any

from django.utils.text import slugify

from aria.categories.models import Category
from aria.categories.tests.utils import create_category
from aria.product_attributes.models import Size, Variant
from aria.product_attributes.tests.utils import create_size, create_variant
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product, ProductOption
from aria.suppliers.models import Supplier
from aria.suppliers.tests.utils import get_or_create_supplier


def create_product(
    *,
    product_name: str = "Test product",
    slug: str | None = None,
    status: ProductStatus = ProductStatus.AVAILABLE,
    unit: ProductUnit = ProductUnit.PCS,
    category_name: str | None = None,
    category_parent: Category | None = None,
    supplier: Supplier | None = None,
    options: list[ProductOption] | None = None,
    quantity: int = 1,
    **kwargs: dict[str, Any],
) -> Product | list[Product]:
    """
    Test util that creates a product instance.
    """

    # Validate that provided slug is unique.
    if slug is not None:
        assert not Product.objects.filter(slug=slug).exists()

    if supplier is None:
        supplier = get_or_create_supplier()

    created_products = []
    for i in range(quantity):
        product = Product.objects.create(
            name=f"{product_name} {i}",
            supplier=supplier,
            status=status,
            slug=slug or slugify(product_name),
            unit=unit,
            vat_rate=kwargs.get("vat_rate", 0.25),
            **kwargs,
        )

        if category_name is not None:
            if category_parent is None:
                category_parent = create_category(name=f"Parent - {category_name}")
            category = create_category(name=category_name, parent=category_parent)
        else:
            parent = create_category(name="Parent")
            category = create_category(parent=parent)

        product.categories.set([category])
        created_products.append(product)

        if options is None:
            create_product_option(product=product)

    if quantity == 1:
        return created_products[0]

    return created_products


def create_product_option(
    *,
    product: Product,
    variant: Variant | None = None,
    size: Size | None = None,
    gross_price: Decimal = Decimal(200.00),
    status: ProductStatus = ProductStatus.AVAILABLE,
) -> ProductOption:
    """
    Test util that creates a product option instance.
    """

    if variant is None:
        variant = create_variant()

    if size is None:
        size = create_size(width=Decimal("100.0"), height=Decimal("100.0"))

    product_option, _created = ProductOption.objects.get_or_create(
        product=product,
        variant=variant,
        size=size,
        gross_price=gross_price,
        status=status,
    )

    return product_option
