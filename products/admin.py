from django.contrib import admin

from products.models import Product, ProductVariant, Color, ProductFile, ProductImage, ProductSize, ProductSiteState, Size, ProductOptions, Variant

class SizeAdmin(admin.ModelAdmin):
    model = Size
    # list_display = ('height', 'width', 'depth', 'circumference')
    # ordering = ('height', 'width', 'depth', 'circumference')

class VariantAdmin(admin.ModelAdmin):
    model = Variant
class ColorAdmin(admin.ModelAdmin):
    model = Color
    list_display = ('name', 'color_hex')
    ordering = ['name']


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductSizeInline(admin.StackedInline):
    model = ProductSize


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant

class ProductSiteStateInline(admin.StackedInline):
    model = ProductSiteState


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'slug')
    list_filter = ('status', 'supplier__name', 'category',)
    filter_horizontal = ('sites', 'colors', 'category',)
    ordering = ['name']
    inlines = [ProductSiteStateInline, ProductImageInline, ProductFileInline, ProductVariantInline, ProductSizeInline]


class ProductOptionsAdmin(admin.ModelAdmin):
    model = ProductOptions
    list_display = ('product', 'variant', 'size')


admin.site.register(Color, ColorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductOptions, ProductOptionsAdmin)
admin.site.register(Variant, VariantAdmin)
