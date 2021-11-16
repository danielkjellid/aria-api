from django.contrib import admin

from products.models import Product, Color, ProductFile, ProductImage, ProductSiteState, Size, ProductOption, Variant


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductOptionsInline(admin.StackedInline):
    model = ProductOption


class ProductSiteStateInline(admin.StackedInline):
    model = ProductSiteState


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_hex')
    ordering = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('id', 'name', 'status')
    ordering = ['-id']


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    search_fields = ('product__name', 'variant__name')
    list_display = ('product', 'variant', 'size')
    ordering = ('-id', 'product__name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ('supplier__name', 'name', 'slug')
    list_display = ('name', 'status', 'slug')
    list_filter = ('status', 'supplier__name', 'category',)
    filter_horizontal = ('sites', 'colors', 'category',)
    ordering = ['-id']
    inlines = [ProductSiteStateInline, ProductImageInline, ProductFileInline, ProductOptionsInline]

