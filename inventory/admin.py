from django.contrib import admin

from inventory.models import Category, SubCategory, Product, ProductImage
                                

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


class ProductSizeInline(admin.TabularInline):
    model = Product.sizes.through


class ProductColorInline(admin.TabularInline):
    model = Product.colors.through


class ProductRoomInline(admin.TabularInline):
    model = Product.rooms.through


class ProductStyleInline(admin.TabularInline):
    model = Product.styles.through


class ProductApplicationInline(admin.TabularInline):
    model = Product.application.through


class ProductMaterialInline(admin.TabularInline):
    model = Product.material.through


class ProductImageInline(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'net_price')
    list_filer = ('status', 'category', 'can_be_purchased_online')
    ordering = ('name', 'category')
    inlines = (ProductSizeInline, ProductColorInline, ProductRoomInline, ProductStyleInline, ProductApplicationInline, ProductMaterialInline, ProductImageInline)

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)