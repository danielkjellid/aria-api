from django.contrib import admin
from suppliers.models import Supplier

class SupplierAdmin(admin.ModelAdmin):
    model = Supplier
    list_display = ('name', 'contact_email', 'origin_country')
    filter_horizontal = ('sites', )
    list_filter = ['is_active']
    ordering = ['name']

admin.site.register(Supplier, SupplierAdmin)