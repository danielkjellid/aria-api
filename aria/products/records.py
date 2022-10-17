from decimal import Decimal

from pydantic import BaseModel

from aria.categories.records import CategoryDetailRecord
from aria.core.records import BaseArrayFieldLabelRecord, BaseHeaderImageRecord
from aria.products.enums import ProductMaterials


class ProductSupplierRecord(BaseModel):
    id: int
    name: str
    origin_country: str
    origin_country_flag: str


class ProductColorRecord(BaseModel):
    id: int
    name: str
    color_hex: str


class ProductVariantRecord(BaseModel):
    id: int
    name: str
    image: str | None
    thumbnail: str | None
    is_standard: bool = False


class ProductSizeRecord(BaseModel):
    id: int
    width: Decimal | None = None
    height: Decimal | None = None
    depth: Decimal | None = None
    circumference: Decimal | None = None
    name: str


class ProductDiscountRecord(BaseModel):
    is_discounted: bool
    discounted_gross_price: Decimal
    discounted_gross_percentage: Decimal | None
    maximum_sold_quantity: int | None
    remaining_quantity: int | None


class ProductOptionRecord(BaseModel):
    id: int
    gross_price: Decimal
    status: str
    variant_id: int | None
    size_id: int | None


class ProductOptionDetailRecord(BaseModel):
    id: int
    discount: ProductDiscountRecord | None
    gross_price: Decimal
    status: str
    variant: ProductVariantRecord | None
    size: ProductSizeRecord | None


class ProductFileRecord(BaseModel):
    id: int
    product_id: int
    name: str
    file: str | None


class ProductShapeRecord(BaseModel):
    id: int
    name: str
    image: str | None


class ProductRecord(BaseModel):
    id: int
    name: str
    supplier: ProductSupplierRecord
    status: str
    slug: str
    search_keywords: str | None
    description: str
    unit: str
    vat_rate: float
    available_in_special_sizes: bool = False
    absorption: float | None = None
    is_imported_from_external_source: bool = False
    rooms: list[BaseArrayFieldLabelRecord] = []
    materials: list[BaseArrayFieldLabelRecord] = []
    thumbnail: str | None


class ProductDetailRecord(ProductRecord):
    from_price: Decimal
    display_price: bool
    can_be_picked_up: bool
    can_be_purchased_online: bool
    colors: list[ProductColorRecord] = []
    shapes: list[ProductShapeRecord] = []
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
    supplier: ProductSupplierRecord
    thumbnail: str | None = None
    display_price: bool
    from_price: Decimal
    discount: ProductDiscountRecord | None
    materials: list[BaseArrayFieldLabelRecord]
    rooms: list[BaseArrayFieldLabelRecord]
    colors: list[ProductColorRecord]
    shapes: list[ProductShapeRecord]
    variants: list[ProductVariantRecord]
