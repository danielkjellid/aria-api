from aria.products.enums import ProductUnit
from aria.products.models import Product
from aria.products.records import (
    ProductColorRecord,
    ProductListRecord,
    ProductRecord,
    ProductShapeRecord,
    ProductSupplierRecord,
    ProductVariantRecord,
)
from aria.products.selectors.discounts import product_get_active_discount
from aria.products.selectors.pricing import product_get_price_from_options

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
