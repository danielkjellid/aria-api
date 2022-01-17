from django.contrib import admin

from aria.products.models import (
    Color,
    Product,
    ProductFile,
    ProductImage,
    ProductOption,
    ProductSiteState,
    Size,
    Variant,
    Shape,
)


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductOptionsInline(admin.StackedInline):
    model = ProductOption


class ProductSiteStateInline(admin.StackedInline):
    model = ProductSiteState


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color_hex")
    ordering = ["name"]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("width", "height", "depth", "circumference")
    ordering = ("width", "height")


@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ("name", "image")
    ordering = ("name",)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name", "image", "is_standard")
    list_filter = ("is_standard",)
    ordering = ["-id"]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    search_fields = ("product__name", "variant__name")
    list_display = ("product", "variant", "size")
    ordering = ("-id", "product__name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ("supplier__name", "name", "slug")
    list_display = ("name", "status", "slug")
    list_filter = (
        "status",
        "supplier__name",
        "category",
    )
    filter_horizontal = (
        "sites",
        "colors",
        "category",
        "shapes",
    )
    ordering = ["-id"]
    inlines = [
        ProductSiteStateInline,
        ProductImageInline,
        ProductFileInline,
        ProductOptionsInline,
    ]
