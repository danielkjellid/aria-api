from django.contrib import admin

from aria.product_categorization.models import Category, SubCategory


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name", "ordering", "slug", "display_in_navbar", "is_active")
    filter_horizontal = ("sites",)
    list_filter = ("is_active", "display_in_navbar")
    ordering = ("ordering", "name")


class SubCategoryAdmin(admin.ModelAdmin):
    model = SubCategory
    list_display = ("parent", "name", "ordering", "slug", "is_active")
    filter_horizontal = ("sites",)
    list_filter = ["is_active"]
    ordering = ("parent", "ordering")


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
