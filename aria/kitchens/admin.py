from django.contrib import admin

from aria.kitchens.models import (
    Decor,
    Kitchen,
    Plywood,
)


@admin.register(Kitchen)
class KitchenAdmin(admin.ModelAdmin):
    model = Kitchen
    list_display = ("name", "status", "slug")
    list_filter = (("status"),)


# TODO: Remove admins bellow
@admin.register(Decor)
class KitchenDecorAdmin(admin.ModelAdmin):
    model = Decor


@admin.register(Plywood)
class KitchenPlywoodAdmin(admin.ModelAdmin):
    model = Plywood
