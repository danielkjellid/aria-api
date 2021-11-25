from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext, gettext_lazy as _

from aria.users.models import User


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = "__all__"


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
