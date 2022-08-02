from django.contrib import admin

from aria.discounts.models import ProductDiscount


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    model = ProductDiscount
    list_display = (
        "name",
        "description",
        "slug",
    )
    filter_horizontal = ("products",)
