from django.contrib import admin

from aria.kitchens.models import (
    Decor,
    ExclusiveColor,
    Kitchen,
    LaminateColor,
    Plywood,
    SilkColor,
    TrendColor,
)


class KitchenAdmin(admin.ModelAdmin):
    model = Kitchen
    list_display = ("name", "status", "slug")
    list_filter = (("status"),)


admin.site.register(Kitchen, KitchenAdmin)


# to be removed
class KitchenSilkAdmin(admin.ModelAdmin):
    model = SilkColor


class KitchenDecorAdmin(admin.ModelAdmin):
    model = Decor


class KitchenPlywoodAdmin(admin.ModelAdmin):
    model = Plywood


class KitchenLaminateAdmin(admin.ModelAdmin):
    model = LaminateColor


class KitchenExclusiveAdmin(admin.ModelAdmin):
    model = ExclusiveColor


class KitchenTrendAdmin(admin.ModelAdmin):
    model = TrendColor


admin.site.register(SilkColor, KitchenSilkAdmin)
admin.site.register(Decor, KitchenDecorAdmin)
admin.site.register(Plywood, KitchenPlywoodAdmin)
admin.site.register(LaminateColor, KitchenLaminateAdmin)
admin.site.register(ExclusiveColor, KitchenExclusiveAdmin)
admin.site.register(TrendColor, KitchenTrendAdmin)
