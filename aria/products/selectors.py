import itertools
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.db.models import Min, Prefetch, Q

from aria.categories.models import Category
from aria.categories.selectors import category_tree_active_list_for_product
from aria.core.decorators import cached
from aria.core.models import BaseQuerySet
from aria.core.selectors import base_header_image_record
from aria.discounts.models import Discount
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.filters import ProductSearchFilter
from aria.products.models import Product, ProductOption
from aria.products.records import (
    ProductColorRecord,
    ProductDetailRecord,
    ProductDiscountRecord,
    ProductFileRecord,
    ProductListRecord,
    ProductOptionRecord,
    ProductRecord,
    ProductShapeRecord,
    ProductSizeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.schemas.filters import ProductListFilters


#####################
# Records selectors #
#####################


def product_record(product: Product) -> ProductRecord:
    """
    Get the record representation for a single product instance.
    """

    return ProductRecord(
        id=product.id,
        name=product.name,
        supplier=ProductSupplierRecord(
            id=product.supplier_id,
            name=product.supplier.name,
            origin_country=product.supplier.country_name,
            origin_country_flag=product.supplier.unicode_flag,
        ),
        status=product.status_display,
        slug=product.slug,
        search_keywords=product.search_keywords,
        description=product.description,
        unit=ProductUnit(product.unit).label,
        vat_rate=product.vat_rate,
        available_in_special_sizes=product.available_in_special_sizes,
        absorption=product.absorption,
        is_imported_from_external_source=product.is_imported_from_external_source,
        materials=product.materials_display,
        rooms=product.rooms_display,
        thumbnail=product.thumbnail.url if product.thumbnail else None,
    )


def product_list_record(product: Product) -> ProductListRecord:
    """
    Get the record representation for a list of products. Needs to be
    used with a product preloaded for listing. E.g. with the
    .preload_for_list() queryset manager method.
    """

    assert hasattr(
        product, "available_options_unique_variants"
    ), "Please use the product_list_record alongside prefetched values."

    assert hasattr(
        product, "annotated_from_price"
    ), "Please use the product_list_record alongside prefetched values."

    assert hasattr(
        product, "active_discounts"
    ), "Please use the product_list_record alongside prefetched values."

    available_options = getattr(product, "available_options_unique_variants")

    return ProductListRecord(
        id=product.id,
        name=product.name,
        slug=product.slug,
        status=product.status_display,
        unit=product.unit_display,
        supplier=ProductSupplierRecord(
            id=product.supplier.id,
            name=product.supplier.name,
            origin_country=product.supplier.country_name,
            origin_country_flag=product.supplier.unicode_flag,
        ),
        thumbnail=product.thumbnail.url if product.thumbnail else None,
        display_price=product.display_price,
        from_price=product_get_price_from_options(product=product),
        discount=product_get_active_discount(product=product),
        materials=product.materials_display,
        rooms=product.rooms_display,
        colors=[
            ProductColorRecord(id=color.id, name=color.name, color_hex=color.color_hex)
            for color in product.colors.all()
        ],
        shapes=[
            ProductShapeRecord(id=shape.id, name=shape.name, image=shape.image.url)
            for shape in product.shapes.all()
        ],
        variants=[
            ProductVariantRecord(
                id=option.variant.id,
                name=option.variant.name,
                image=option.variant.image.url if option.variant.image else None,
                thumbnail=option.variant.thumbnail.url
                if option.variant.thumbnail
                else None,
                is_standard=option.variant.is_standard,
            )
            for option in available_options
            if option.variant
        ],
    )


#####################
# Options selectors #
#####################


def product_get_price_from_options(*, product: Product) -> Decimal:
    """
    Get a product's from price based on lowest options price
    available.
    """

    annotated_price = getattr(product, "annotated_from_price", None)

    # If annotated value already exists, return that without taking
    # a roundtrip to the db.
    if annotated_price is not None:
        return Decimal(annotated_price)

    # Aggregate lowest gross price based on a product's options.
    lowest_option_price = product.options.available().aggregate(
        price=Min("gross_price", filter=Q(gross_price__gt=0))
    )["price"]

    return Decimal(lowest_option_price) if lowest_option_price else Decimal("0.00")


def product_options_list_for_product(*, product: Product) -> list[ProductOptionRecord]:
    """
    Get a full representation of a product options connected to a single product
    instance.

    If possible, use the manager method with_available_options_and_options_discounts()
    on the product queryset before sending in the product instance arg.
    """

    # Attempt to get prefetched product options if they exist.
    prefetched_product_options = getattr(product, "available_options", None)

    if prefetched_product_options is not None:
        options = prefetched_product_options
    else:
        # If prefetched value does not exist, fall back to a queryset.
        options = (
            product.options.filter(status=ProductStatus.AVAILABLE)
            .select_related(
                "variant",
                "size",
            )
            .prefetch_related(
                Prefetch(
                    "discounts",
                    queryset=Discount.objects.active(),
                    to_attr="active_discounts",
                )
            )
        )

    return [
        ProductOptionRecord(
            id=option.id,
            discount=product_option_get_active_discount(product_option=option),
            gross_price=option.gross_price,
            status=option.status_display,
            variant=ProductVariantRecord(
                id=option.variant.id,
                name=option.variant.name,
                image=option.variant.image.url if option.variant.image else None,
                thumbnail=option.variant.thumbnail.url
                if option.variant.thumbnail
                else None,
                is_standard=option.variant.is_standard,
            )
            if option.variant
            else None,
            size=ProductSizeRecord(
                id=option.size.id,
                width=option.size.width,
                height=option.size.height,
                depth=option.size.depth,
                circumference=option.size.circumference,
                name=option.size.name,
            )
            if option.size
            else None,
        )
        for option in options
    ]


###############################
# Product discounts selectors #
###############################


def _calculate_discounted_price(*, price: Decimal, discount: Discount) -> Decimal:
    """
    Calculate a discounted price.

    Will set the price to a discount's discount_gross_price, or
    calculate price based on discount percentage if that is defined
    instead.
    """

    if discount.discount_gross_price:
        discounted_gross_price = discount.discount_gross_price
    elif discount.discount_gross_percentage:
        discounted_gross_price = Decimal(price) * (
            Decimal("1") - discount.discount_gross_percentage
        )

    discounted_gross_price = discounted_gross_price.quantize(
        Decimal(".01"), rounding=ROUND_HALF_UP
    )

    return discounted_gross_price


def product_calculate_discounted_price(
    *, product: Product, discount: Discount
) -> Decimal:
    """
    Get discounted price for a product.
    """

    return _calculate_discounted_price(
        price=product_get_price_from_options(product=product), discount=discount
    )


def product_option_calculate_discounted_price(
    *, option: ProductOption, discount: Discount
) -> Decimal:
    """
    Get discounted price for an option.
    """

    return _calculate_discounted_price(price=option.gross_price, discount=discount)


def product_get_active_discount(*, product: Product) -> ProductDiscountRecord | None:
    """
    Get an active discount for a specific product. A discount can either be
    on the product level, or it can be for a specific option. This selector
    will combine them.

    This means that if there is a discount for a single option related to a
    product, this selector will "catch" it, and append it.

    If used in a loop, it's preferable to use it alongside the
    .preload_for_list() queryset manager method.
    """

    prefetched_active_product_discounts = getattr(product, "active_discounts", None)
    prefetched_active_options_discounts = getattr(
        product, "available_options_with_discounts", None
    )

    active_discounts = []

    # Use prefetched attributes if available.
    if prefetched_active_product_discounts is not None:
        active_discounts = prefetched_active_product_discounts

    if prefetched_active_options_discounts is not None and len(active_discounts) == 0:
        active_options_discounts = []

        if len(prefetched_active_options_discounts) > 0:
            # Extract a list of discounts associated with the options.
            active_options_discounts = list(
                itertools.chain(
                    *[
                        option.active_discounts
                        for option in prefetched_active_options_discounts
                        if len(option.active_discounts) > 0
                    ]
                )
            )

        active_discounts = active_discounts + active_options_discounts

    # Fall back to retrieving data from queryset if prefetched attributes
    # isn't available.
    if (
        prefetched_active_product_discounts is None
        and prefetched_active_options_discounts is None
    ):
        product_discounts = list(product.discounts.active())
        options_discounts = []

        options = product.options.available().prefetch_related(
            Prefetch(
                "discounts",
                queryset=Discount.objects.active(),
                to_attr="active_discounts",
            )
        )

        if len(options) > 0:
            # Extract a list over discounts associated with the options.
            options_discounts = list(
                itertools.chain(
                    *[
                        option.active_discounts  # type: ignore
                        for option in options
                        if len(option.active_discounts) > 0  # type: ignore
                    ]
                )
            )

        active_discounts = product_discounts + options_discounts

    if len(active_discounts) == 0:
        return None

    discount = active_discounts[0]

    return ProductDiscountRecord(
        is_discounted=True,
        discounted_gross_price=product_calculate_discounted_price(
            product=product, discount=discount
        ),
        discounted_gross_percentage=discount.discount_gross_percentage
        if discount.discount_gross_percentage
        else None,
        maximum_sold_quantity=discount.maximum_sold_quantity
        if discount.maximum_sold_quantity
        else None,
        remaining_quantity=(
            discount.maximum_sold_quantity - discount.total_sold_quantity
        )
        if discount.maximum_sold_quantity and discount.total_sold_quantity
        else None,
    )


def product_option_get_active_discount(
    *, product_option: ProductOption
) -> ProductDiscountRecord | None:
    """
    Get an active discount for a specific option. A discount can either be
    on the product level, or it can be for a specific option. This selector
    will combine them.

    This means that if there is a discount for a product, all related options
    will inherit that discount and append it, unless there is specified a more
    specific discount on the option itself.
    """

    prefetched_active_product_discounts = getattr(
        product_option.product, "active_discounts", None
    )
    prefetched_active_options_discounts = getattr(
        product_option, "active_discounts", None
    )

    active_discounts = []

    # Attempt to find discounts through prefetched attributes first.
    if prefetched_active_options_discounts is not None:
        active_discounts = prefetched_active_options_discounts

    if prefetched_active_product_discounts is not None and len(active_discounts) == 0:
        active_discounts = prefetched_active_product_discounts

    # Fall back to retrieving data from queryset if prefetched attributes
    # isn't available.
    if (
        prefetched_active_product_discounts is None
        and prefetched_active_options_discounts is None
    ):
        active_options_discounts = list(product_option.discounts.active())
        active_product_discounts = list(product_option.product.discounts.active())

        active_discounts = active_options_discounts + active_product_discounts

    if len(active_discounts) == 0:
        return None

    discount = active_discounts[0]

    return ProductDiscountRecord(
        is_discounted=True,
        discounted_gross_price=product_option_calculate_discounted_price(
            option=product_option, discount=discount
        ),
        discounted_gross_percentage=discount.discount_gross_percentage
        if discount.discount_gross_percentage
        else None,
        maximum_sold_quantity=discount.maximum_sold_quantity
        if discount.maximum_sold_quantity
        else None,
        remaining_quantity=(
            discount.maximum_sold_quantity - discount.total_sold_quantity
        )
        if discount.maximum_sold_quantity and discount.total_sold_quantity
        else None,
    )


#####################
# Product selectors #
#####################


def product_detail(
    *, product_id: int | None = None, product_slug: str | None = None
) -> ProductDetailRecord | None:
    """
    Get the detailed representation of a single product based on either
    id or slug, although one of them has to be provided.

    Be careful to not run this in a loop unless absolutely needed. It
    already does quite a few queries, and will to that amount per loop
    iteration.
    """

    product = (
        Product.objects.filter(Q(id=product_id) | Q(slug=product_slug))  # type: ignore
        .with_active_categories()
        .with_colors()
        .with_shapes()
        .with_files()
        .with_available_options_and_option_discounts()
        .with_active_product_discounts()
        .annotate_from_price()
        .first()
    )

    if not product:
        return None

    categories = category_tree_active_list_for_product(product=product)
    options = product_options_list_for_product(product=product)

    product_base_record = product_record(product=product)

    record = ProductDetailRecord(
        **product_base_record.dict(),
        categories=categories,
        from_price=product_get_price_from_options(product=product),
        display_price=product.display_price,
        can_be_picked_up=product.can_be_picked_up,
        can_be_purchased_online=product.can_be_purchased_online,
        colors=[
            ProductColorRecord(id=color.id, name=color.name, color_hex=color.color_hex)
            for color in product.colors.all()
        ],
        shapes=[
            ProductShapeRecord(
                id=shape.id,
                name=shape.name,
                image=shape.image.url if shape.image else None,
            )
            for shape in product.shapes.all()
        ],
        files=[
            ProductFileRecord(
                id=file.id, name=file.name, file=file.file.url if file.file else None
            )
            for file in product.files.all()
        ],
        images=[
            base_header_image_record(instance=image) for image in product.images.all()
        ],
        options=options,
    )

    return record


def product_list_for_sale_for_qs(
    *,
    products: BaseQuerySet["Product"] | None,
    filters: ProductListFilters | dict[str, Any] | None,
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products based on given queryset. The
    ProductListRecord is a record of mutual properties for use whenever we
    show a list of products frontend.
    """

    filters = filters or {}

    if products is not None:
        qs = products.preload_for_list().order_by("-created_at")  # type: ignore

    else:
        qs = Product.objects.available().preload_for_list().order_by("-created_at")  # type: ignore # pylint: disable=line-too-long

    filtered_qs = ProductSearchFilter(filters, qs).qs

    return [product_list_record(product=product) for product in filtered_qs]


def product_list(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products.
    """

    products = Product.objects.all()

    return product_list_for_sale_for_qs(products=products, filters=filters)


def product_list_for_sale(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products for sale.
    """

    products = Product.objects.available()

    return product_list_for_sale_for_qs(products=products, filters=filters)


def _product_list_for_sale_cache_key(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> str:
    return f"products.for_sale.filters={filters}"


@cached(key=_product_list_for_sale_cache_key, timeout=5 * 60)
def product_list_for_sale_from_cache(
    *, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products for sale from cache.
    """

    return product_list_for_sale(filters=filters)


def product_list_by_category(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products belonging to the given category.
    """

    products_by_category = Product.objects.by_category(category)

    return product_list_for_sale_for_qs(products=products_by_category, filters=filters)


def _product_list_by_category_cache_key(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> str:
    return f"products.category_id={category.id}.filters={filters}"


@cached(key=_product_list_by_category_cache_key, timeout=5 * 60)
def product_list_by_category_from_cache(
    *, category: Category, filters: ProductListFilters | dict[str, Any] | None
) -> list[ProductListRecord]:
    """
    Returns a filterable list of products belonging to the given category
    from cache.
    """

    return product_list_by_category(category=category, filters=filters)
