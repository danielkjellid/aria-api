from django.contrib import admin

from aria.discounts.models import Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    model = Discount
    list_display = (
        "name",
        "description",
        "slug",
    )
    filter_horizontal = ("products",)
