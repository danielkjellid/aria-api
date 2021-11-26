from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from aria.users.models import User


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = "__all__"


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
