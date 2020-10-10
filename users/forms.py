from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import User


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = '__all__'


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = '__all__'
