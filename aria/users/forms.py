from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)

from aria.users.models import User
from django import forms
from django.utils.translation import gettext, gettext_lazy as _


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = "__all__"


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
