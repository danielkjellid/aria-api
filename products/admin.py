from django.contrib import admin

from products.models import Product, ProductVariant, ProductColor, ProductFile, ProductImage, ProductSize, ProductSiteState, Size

class SizeAdmin(admin.ModelAdmin):
    model = Size
    # list_display = ('height', 'width', 'depth', 'circumference')
    # ordering = ('height', 'width', 'depth', 'circumference')

class ProductColorAdmin(admin.ModelAdmin):
    model = ProductColor
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


admin.site.register(ProductColor, ProductColorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)