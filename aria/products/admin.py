from django.contrib import admin

from aria.products.models import Product, ProductFile, ProductImage, ProductOption


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductOptionsInline(admin.StackedInline):
    model = ProductOption


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
        "categories",
    )
    filter_horizontal = (
        "colors",
        "categories",
        "new_materials",
        "new_rooms",
        "shapes",
    )
    ordering = ["-id"]
    inlines = [
        ProductImageInline,
        ProductFileInline,
        ProductOptionsInline,
    ]
