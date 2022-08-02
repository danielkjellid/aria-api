from django.contrib import admin

from aria.discounts.models import DiscountProduct


@admin.register(DiscountProduct)
class DiscountProductAdmin(admin.ModelAdmin):
    model = DiscountProduct
    list_display = (
        "name",
        "description",
        "slug",
    )
    filter_horizontal = ("products",)
