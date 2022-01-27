from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from aria.categories.models import Category

admin.site.register(Category, MPTTModelAdmin)
