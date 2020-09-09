from django.contrib import admin

from inventory.models import Category, SubCategory, Product, ProductImage, Supplier, ProductSize, ProductColor, ProductApplication, ProductMaterial, ProductRoom, ProductStyle
                                

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


class ProductRoomAdmin(admin.ModelAdmin):
    model = ProductRoom
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


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'status', 'net_price')
    list_filer = ('status', 'category', 'can_be_purchased_online')
    ordering = ('name', 'category')
    inlines = [ProductImageInline]

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(ProductSize, ProductSizeAdmin)
admin.site.register(ProductColor, ProductColorAdmin)
admin.site.register(ProductRoom, ProductRoomAdmin)
admin.site.register(ProductApplication, ProductApplicationAdmin)
admin.site.register(ProductMaterial, ProductMaterialAdmin)
admin.site.register(Product, ProductAdmin)