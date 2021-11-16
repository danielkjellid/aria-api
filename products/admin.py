from django.contrib import admin

from products.models import Product, Color, ProductFile, ProductImage, ProductSiteState, Size, ProductOption, Variant


class ColorAdmin(admin.ModelAdmin):
    model = Color
    list_display = ('name', 'color_hex')
    ordering = ['name']


class VariantAdmin(admin.ModelAdmin):
    model = Variant


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductOptionsInline(admin.StackedInline):
    model = ProductOption


class ProductSiteStateInline(admin.StackedInline):
    model = ProductSiteState


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'slug')
    list_filter = ('status', 'supplier__name', 'category',)
    filter_horizontal = ('sites', 'colors', 'category',)
    ordering = ['name']
    inlines = [ProductSiteStateInline, ProductImageInline, ProductFileInline, ProductOptionsInline]


class ProductOptionAdmin(admin.ModelAdmin):
    model = ProductOption
    list_display = ('product', 'variant', 'size')


admin.site.register(Color, ColorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(Variant, VariantAdmin)
