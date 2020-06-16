from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_registration.forms import RegistrationForm

from users.models import User


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = '__all__'


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = '__all__'


class UserRegistrationForm(RegistrationForm):

    class Meta(RegistrationForm.Meta):
        model = User