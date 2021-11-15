from django.contrib import admin

from products.models import Product, ProductVariant, Color, ProductFile, ProductImage, ProductSize, ProductSiteState, Size, ProductOption, Variant

class SizeAdmin(admin.ModelAdmin):
    model = Size
    # list_display = ('height', 'width', 'depth', 'circumference')
    # ordering = ('height', 'width', 'depth', 'circumference')

class ProductSizeAdmin(admin.ModelAdmin):
    model = ProductSize

class VariantAdmin(admin.ModelAdmin):
    model = Variant

class ProductVariantAdmin(admin.ModelAdmin):
    model = ProductVariant

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


class ProductOptionAdmin(admin.ModelAdmin):
    model = ProductOption
    list_display = ('product', 'variant', 'size')


admin.site.register(Color, ColorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
