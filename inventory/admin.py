from django.contrib import admin

from inventory.models import Category, SubCategory

admin.site.register(Category)
admin.site.register(SubCategory)