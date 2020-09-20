from django.contrib import admin

from inventory.models import (Category, Product, ProductApplication,
                              ProductColor, ProductImage, ProductMaterial,
                              ProductSize, ProductStyle, ProductVariant,
                              SubCategory, Supplier)


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name', 'ordering', 'slug', 'display_in_navbar', 'is_active')
    list_filter = ('is_active', 'display_in_navbar')
    ordering = ('ordering', 'name')


class SubCategoryAdmin(admin.ModelAdmin):
    model = SubCategory
    list_display = ('parent', 'name', 'ordering', 'slug', 'is_active')
    list_filter = ['is_active']
    ordering = ('parent', 'ordering')


class SupplierAdmin(admin.ModelAdmin):
    model = Supplier
    list_display = ('name', 'contact_email', 'origin_country')
    list_filter = ['is_active']
    ordering = ['name']


class ProductSizeAdmin(admin.ModelAdmin):
    model = ProductSize
    list_display = ('height', 'width', 'depth')
    ordering = ('height', 'width', 'depth')


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


class ProductVariantAdmin(admin.ModelAdmin):
    model = ProductVariant
    list_display = ('product', 'name', 'status', 'additional_cost')
    ordering = ('product', 'name')
    list_filter = ['status']


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'gross_price')
    list_filer = ('status', 'category', 'can_be_purchased_online')
    ordering = ['name']
    inlines = [ProductImageInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductColor, ProductColorAdmin)
admin.site.register(ProductStyle, ProductStyleAdmin)
admin.site.register(ProductApplication, ProductApplicationAdmin)
admin.site.register(ProductMaterial, ProductMaterialAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Product, ProductAdmin)
