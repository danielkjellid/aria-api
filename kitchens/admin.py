from django.contrib import admin
from kitchens.models import Kitchen, KitchenSilkColor, KitchenDecor, KitchenPlywood, KitchenLaminateColor, KitchenExclusiveColor, KitchenTrendColor

class KitchenAdmin(admin.ModelAdmin):
    model = Kitchen
    list_display = ('name', 'status', 'slug')
    list_filter = ('status'),

admin.site.register(Kitchen, KitchenAdmin)

# to be removed
class KitchenSilkAdmin(admin.ModelAdmin):
    model = KitchenSilkColor

class KitchenDecorAdmin(admin.ModelAdmin):
    model = KitchenDecor

class KitchenPlywoodAdmin(admin.ModelAdmin):
    model = KitchenPlywood

class KitchenLaminateAdmin(admin.ModelAdmin):
    model = KitchenLaminateColor

class KitchenExclusiveAdmin(admin.ModelAdmin):
    model = KitchenExclusiveColor

class KitchenTrendAdmin(admin.ModelAdmin):
    model = KitchenTrendColor

admin.site.register(KitchenSilkColor, KitchenSilkAdmin)
admin.site.register(KitchenDecor, KitchenDecorAdmin)
admin.site.register(KitchenPlywood, KitchenPlywoodAdmin)
admin.site.register(KitchenLaminateColor, KitchenLaminateAdmin)
admin.site.register(KitchenExclusiveColor, KitchenExclusiveAdmin)
admin.site.register(KitchenTrendColor, KitchenTrendAdmin)
