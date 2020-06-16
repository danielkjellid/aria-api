from django.contrib import admin
from django.urls import include, path

from django_registration.backends.activation.views import RegistrationView
from users.forms import UserRegistrationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bruker/registrer/', RegistrationView.as_view(form_class=UserRegistrationForm, success_url='/'), name='django_registration-register'),
    path('bruker/', include('django_registration.backends.activation.urls')),
    path('bruker/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
