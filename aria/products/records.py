from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

from aria.categories.records import CategoryDetailRecord
from aria.core.records import BaseArrayFieldLabelRecord
from aria.files.records import BaseHeaderImageRecord
from aria.product_attributes.records import (
    ColorDetailRecord,
    ShapeDetailRecord,
    SizeDetailRecord,
    SizeRecord,
    VariantDetailRecord,
)
from aria.products.enums import ProductStatus
from aria.suppliers.records import SupplierRecord

if TYPE_CHECKING:
    from aria.products.models import Product


class ProductSupplierRecord(BaseModel):
    id: int
    name: str
    origin_country: str
    origin_country_flag: str


class ProductDiscountRecord(BaseModel):
    is_discounted: bool
    discounted_gross_price: Decimal
    discounted_gross_percentage: Decimal | None
    maximum_sold_quantity: int | None
    remaining_quantity: int | None


class ProductOptionRecord(BaseModel):
    id: int
    gross_price: Decimal
    status: ProductStatus
    variant_id: int | None
    size_id: int | None


class OptionRecord(BaseModel):
    gross_price: Decimal
    status: ProductStatus
    variant_id: int | None
    size: SizeRecord | None


class ProductOptionDetailRecord(BaseModel):
    id: int
    discount: ProductDiscountRecord | None
    gross_price: Decimal
    status: str
    variant: VariantDetailRecord | None
    size: SizeDetailRecord | None


class ProductFileRecord(BaseModel):
    id: int
    product_id: int
    name: str
    file: str | None


class ProductImageRecord(BaseModel):
    id: int
    product_id: int
    image_url: str | None


class ProductRecord(BaseModel):
    id: int
    name: str
    supplier: SupplierRecord
    status: str
    slug: str
    search_keywords: str | None
    description: str
    unit: str
    vat_rate: Decimal
    available_in_special_sizes: bool = False
    absorption: float | None = None
    is_imported_from_external_source: bool = False
    rooms: list[BaseArrayFieldLabelRecord] = []
    materials: list[BaseArrayFieldLabelRecord] = []
    thumbnail: str | None

    @classmethod
    def from_product(cls, product: Product) -> ProductRecord:
        """
        Generate product record from model.
        """
        return cls(
            id=product.id,
            name=product.name,
            supplier=SupplierRecord.from_supplier(product.supplier),
            status=product.status_display,
            slug=product.slug,
            search_keywords=product.search_keywords,
            description=product.description,
            unit=product.unit_display,
            vat_rate=Decimal(product.vat_rate),
            available_in_special_sizes=product.available_in_special_sizes,
            absorption=product.absorption,
            is_imported_from_external_source=product.is_imported_from_external_source,
            materials=product.materials_display,
            rooms=product.rooms_display,
            thumbnail=product.thumbnail.url if product.thumbnail else None,
        )


class ProductDetailRecord(ProductRecord):
    from_price: Decimal
    display_price: bool
    can_be_picked_up: bool
    can_be_purchased_online: bool
    colors: list[ColorDetailRecord] = []
    shapes: list[ShapeDetailRecord] = []
    categories: list[CategoryDetailRecord]
    options: list[ProductOptionDetailRecord] = []
    images: list[BaseHeaderImageRecord] = []
    files: list[ProductFileRecord] = []


class ProductListRecord(BaseModel):
    id: int
    name: str
    slug: str
    unit: str
    status: str
    supplier: SupplierRecord
    image380x575_url: str | None = None
    display_price: bool
    from_price: Decimal
    discount: ProductDiscountRecord | None
    materials: list[BaseArrayFieldLabelRecord]
    rooms: list[BaseArrayFieldLabelRecord]
    colors: list[ColorDetailRecord]
    shapes: list[ShapeDetailRecord]
    variants: list[VariantDetailRecord]

    @classmethod
    def from_product(
        cls, product: Product, *, discount: ProductDiscountRecord | None = None
    ) -> ProductListRecord:
        """
        Generate ProductListRecord from product model.
        """

        missing_prefetched_attrs_msg = "Please use the ProductListRecord alongside prefetched values (e.g. with the .preload_for_list() manager method."

        assert hasattr(
            product, "available_options_unique_variants"
        ), missing_prefetched_attrs_msg
        assert hasattr(product, "annotated_from_price"), missing_prefetched_attrs_msg
        assert hasattr(product, "active_discounts"), missing_prefetched_attrs_msg

        available_options = getattr(product, "available_options_unique_variants")

        return cls(
            id=product.id,
            name=product.name,
            slug=product.slug,
            status=product.status_display,
            unit=product.unit_display,
            supplier=SupplierRecord.from_supplier(product.supplier),
            image380x575_url=product.image380x575_url,
            display_price=product.display_price,
            from_price=product.from_price,
            discount=discount,
            materials=product.materials_display,
            rooms=product.rooms_display,
            colors=[
                ColorDetailRecord.from_color(color) for color in product.colors.all()
            ],
            shapes=[
                ShapeDetailRecord.from_shape(shape) for shape in product.shapes.all()
            ],
            variants=[
                VariantDetailRecord.from_variant(option.variant)
                for option in available_options
                if option.variant
            ],
        )
