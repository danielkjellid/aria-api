from django.contrib import admin

from products.models import Product, ProductVariant, ProductApplication, ProductColor, ProductFile, ProductImage, ProductVariantSize, ProductSiteState, ProductMaterial, ProductStyle, Size

class SizeAdmin(admin.ModelAdmin):
    model = Size
    # list_display = ('height', 'width', 'depth', 'circumference')
    # ordering = ('height', 'width', 'depth', 'circumference')

class ProductColorAdmin(admin.ModelAdmin):
    model = ProductColor
    list_display = ('name', 'color_hex')
    ordering = ['name']


class ProductStyleAdmin(admin.ModelAdmin):
    model = ProductStyle
    list_display = ['name']
    ordering = ['name']


class ProductApplicationAdmin(admin.ModelAdmin):
    model = ProductApplication
    list_display = ['name']
    ordering = ['name']


class ProductMaterialAdmin(admin.ModelAdmin):
    model = ProductMaterial
    list_display = ['name']
    ordering = ['name']


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductFileInline(admin.StackedInline):
    model = ProductFile


class ProductVariantSizeInline(admin.StackedInline):
    model = ProductVariantSize


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant

class ProductSiteStateInline(admin.StackedInline):
    model = ProductSiteState  


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'slug')
    list_filter = ('status', 'supplier__name', 'category',)
    filter_horizontal = ('sites', 'materials', 'applications', 'styles', 'colors', 'category',)
    ordering = ['name']
    inlines = [ProductSiteStateInline, ProductImageInline, ProductFileInline, ProductVariantInline, ProductVariantSizeInline]


admin.site.register(ProductColor, ProductColorAdmin)
admin.site.register(ProductStyle, ProductStyleAdmin)
admin.site.register(ProductApplication, ProductApplicationAdmin)
admin.site.register(ProductMaterial, ProductMaterialAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)