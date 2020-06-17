from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django_registration.forms import RegistrationForm

from users.models import User


INPUT_STYLING = 'form-input block w-full text-sm leading-5'
CHECKBOX_STYLING = 'form-checkbox text-gray-800 h-5 w-5'
INPUT_ADD_ON_STYLING = 'form-input flex-1 block w-full px-3 py-2 rounded-none rounded-r-md text-sm leading-5'


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
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'password1',
            'password2',
            'street_address',
            'zip_code',
            'zip_place',
            'subscribed_to_newsletter',
            'allow_personalization',
            'allow_third_party_personalization'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['last_name'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['phone_number'].widget.attrs.update({'class': INPUT_ADD_ON_STYLING})
        self.fields['email'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['password1'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['password2'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['street_address'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['zip_code'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['zip_place'].widget.attrs.update({'class': INPUT_STYLING})
        self.fields['subscribed_to_newsletter'].widget.attrs.update({'class': CHECKBOX_STYLING})
        self.fields['allow_personalization'].widget.attrs.update({'class': CHECKBOX_STYLING})
        self.fields['allow_third_party_personalization'].widget.attrs.update({'class': CHECKBOX_STYLING})
        