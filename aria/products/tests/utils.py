import tempfile
from decimal import Decimal
from typing import Any

from django.utils.text import slugify

from aria.categories.models import Category
from aria.categories.tests.utils import create_category
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Color, Product, ProductOption, Shape, Size, Variant
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
            vat_rate=0.25,
            available_in_special_sizes=available_in_special_sizes,
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


def create_variant(
    *, name: str = "Example variant", is_standard: bool = False
) -> Variant:
    """
    Test util that creates a variant instance.
    """

    variant = Variant.objects.create(name=name, is_standard=is_standard)

    with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
        variant.image = file.name

    variant.save()

    return variant


def create_size(
    width: Decimal | None = None,
    height: Decimal | None = None,
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> Size:
    """
    Test util that creates a size instance.
    """

    if all(param is None for param in (width, height, depth, circumference)):
        raise ValueError("All args cannot be None!")

    size = Size.objects.create(
        width=width, height=height, depth=depth, circumference=circumference
    )

    return size


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


def create_color(*, name: str, color_hex: str) -> Color:
    """
    Test util that creates a color instance.
    """

    color, _created = Color.objects.get_or_create(
        name=name, defaults={"color_hex": color_hex}
    )

    return color


def create_shape(*, name: str) -> Shape:
    """
    Test util that creates a shape instance.
    """

    shape, _created = Shape.objects.get_or_create(name=name)

    with tempfile.NamedTemporaryFile(suffix=".jpg") as file:
        shape.image = file.name

    shape.save()

    return shape
