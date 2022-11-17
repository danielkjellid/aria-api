from django.contrib import admin

from aria.product_attributes.models import Color, Shape, Size, Variant


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color_hex")
    ordering = ["name"]


@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ("name", "image")
    ordering = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("width", "height", "depth", "circumference")
    ordering = ("width", "height")


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("id", "name", "thumbnail", "is_standard")
    list_filter = ("is_standard",)
    ordering = ["-id"]
