from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import UserCreationForm, UserChangeForm
from users.models import User


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('first_name', 'last_name', 'email', 'is_staff', 'is_active')
    list_filter = ('first_name', 'last_name', 'email', 'is_staff', 'is_active')
    fieldsets = (
        ('Personal', {'fields': ('first_name', 'last_name', 'avatar_color', 'date_joined', 'last_login', 'password')}),
        ('Contact', {'fields': ('phone_number', 'email', 'has_confirmed_email', 'street_address', 'zip_code', 'zip_place')}),
        ('Marketing', {'fields': ('disabled_emails', 'subscribed_to_newsletter', 'allow_personalization', 'allow_third_party_personalization', 'acquisition_source', 'site')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name',)


admin.site.register(User, UserAdmin)