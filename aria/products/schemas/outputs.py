from ninja import Schema

from aria.files.records import BaseHeaderImageRecord


class ProductSupplierOutput(Schema):
    name: str
    origin_country: str
    origin_country_flag: str


class ProductVariantOutput(Schema):
    id: int
    name: str
    image80x80_url: str | None
    image380x575_url: str | None


class ProductMaterialOutput(Schema):
    id: int
    name: str


class ProductRoomOutput(Schema):
    id: int
    name: str


class ProductSizeOutput(Schema):
    id: int
    name: str


class ProductCategoryOutput(Schema):
    name: str
    slug: str
    parents: list["ProductCategoryOutput"] | None


class ProductDiscountOutput(Schema):
    is_discounted: bool
    discounted_gross_price: float
    discounted_gross_percentage: float | None
    maximum_sold_quantity: int | None
    remaining_quantity: int | None


class ProductOptionOutput(Schema):
    id: int
    discount: ProductDiscountOutput | None
    gross_price: float
    status: str
    variant: ProductVariantOutput | None
    size: ProductSizeOutput | None


class ProductColorOutput(Schema):
    id: int
    name: str
    color_hex: str


class ProductShapeOutput(Schema):
    id: int
    name: str
    image_url: str | None


class ProductFileOutput(Schema):
    name: str
    file: str | None


class ProductDetailOutput(Schema):
    id: int
    status: str
    unit: str
    name: str
    description: str | None
    absorption: float | None
    from_price: float
    display_price: bool
    can_be_picked_up: bool
    can_be_purchased_online: bool
    categories: list[ProductCategoryOutput] = []
    materials: list[ProductMaterialOutput] = []
    rooms: list[ProductRoomOutput] = []
    available_in_special_sizes: bool = False
    supplier: ProductSupplierOutput
    images: list[BaseHeaderImageRecord] = []
    options: list[ProductOptionOutput] = []
    colors: list[ProductColorOutput] = []
    shapes: list[ProductShapeOutput] = []
    files: list[ProductFileOutput] = []


class ProductListOutput(Schema):
    id: int
    name: str
    slug: str
    unit: str
    supplier: ProductSupplierOutput
    image380x575_url: str | None
    display_price: bool
    from_price: float
    discount: ProductDiscountOutput | None
    colors: list[ProductColorOutput]
    shapes: list[ProductShapeOutput]
    materials: list[ProductMaterialOutput]
    rooms: list[ProductRoomOutput]
    variants: list[ProductVariantOutput]
