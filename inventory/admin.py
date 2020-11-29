from django.contrib import admin

from inventory.models.category import Category, SubCategory
from inventory.models.supplier import Supplier
from inventory.models.product import Product, ProductVariant, ProductFile, ProductImage, ProductApplication, ProductColor, Size, ProductStyle, ProductMaterial, ProductVariantSize
from inventory.models.kitchen import Kitchen, KitchenSilkColor, KitchenDecor, KitchenPlywood, KitchenLaminateColor, KitchenExclusiveColor, KitchenTrendColor


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


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'gross_price', 'slug')
    list_filter = ('status', 'supplier__name', 'category', 'can_be_purchased_online',)
    ordering = ['name']
    inlines = [ProductImageInline, ProductFileInline, ProductVariantInline, ProductVariantSizeInline]


class KitchenAdmin(admin.ModelAdmin):
    model = Kitchen
    list_display = ('name', 'status', 'slug')
    list_filter = ('status'),


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductColor, ProductColorAdmin)
admin.site.register(ProductStyle, ProductStyleAdmin)
admin.site.register(ProductApplication, ProductApplicationAdmin)
admin.site.register(ProductMaterial, ProductMaterialAdmin)
admin.site.register(Product, ProductAdmin)
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