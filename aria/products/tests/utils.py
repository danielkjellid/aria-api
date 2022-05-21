from aria.products.enums import ProductStatus, ProductUnit
from aria.categories.models import Category
from aria.categories.tests.utils import create_category
from aria.products.models import Product, ProductOption, Variant, Size
from django.utils.text import slugify
from aria.suppliers.models import Supplier
from aria.core.tests.utils import create_site
from django.contrib.sites.models import Site
from aria.suppliers.tests.utils import get_or_create_supplier
from decimal import Decimal
import tempfile


def create_product(
    *,
    product_name: str = "Test product",
    slug: str | None = None,
    status: ProductStatus = ProductStatus.AVAILABLE,
    unit: ProductUnit = ProductUnit.PCS,
    available_in_special_sizes: bool = True,
    category_name: str | None = None,
    category_parent: Category | None = None,
    sites: list[Site] | None = None,
    supplier: Supplier | None = None,
    quantity: int = 1,
) -> Product:

    # Validate that provided slug is unique.
    if slug is not None:
        assert not Product.objects.filter(slug=slug).exists()

    if supplier is None:
        supplier = get_or_create_supplier()

    if sites is None:
        sites = [create_site()]

    created_products = []
    for i in range(quantity):
        product = Product.objects.create(
            name=f"{product_name} {i}",
            supplier=supplier,
            status=status,
            slug=slug or slugify(product_name),
            search_keywords="",
            unit=unit,
            vat_rate=0.25,
            available_in_special_sizes=available_in_special_sizes,
        )

        if category_name is not None:
            if category_parent is None:
                category_parent = create_category(name=f"Parent - {category_name}")
            category = create_category(name=category_name, parent=category_parent)
        else:
            parent = create_category(name="Parent")
            category = create_category(parent=parent)

        product.categories.set([category])
        product.sites.set(sites)
        created_products.append(product)

    if quantity == 1:
        return created_products[0]

    return created_products


def create_variant(
    *,
    name: str = "Example variant",
) -> Variant:

    variant = Variant.objects.create(name=name, is_standard=False)

    variant.image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    variant.save()

    return variant


def create_size(
    width: Decimal | None = Decimal(100.00),
    height: Decimal | None = Decimal(100.00),
    depth: Decimal | None = None,
    circumference: Decimal | None = None,
) -> Size:

    if width and height and depth and circumference is None:
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

    if variant is None:
        variant = create_variant()

    if size is None:
        size = create_size()

    product_option = ProductOption.objects.create(
        product=product,
        variant=variant,
        size=size,
        gross_price=gross_price,
        status=status,
    )

    return product_option
