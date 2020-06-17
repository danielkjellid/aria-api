from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from django_registration.backends.one_step.views import RegistrationView
from users.forms import UserAuthenticationForm, UserRegistrationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bruker/registrer/', RegistrationView.as_view(form_class=UserRegistrationForm, success_url='/'), name='django_registration-register'),
    path('bruker/logg-inn/', auth_views.LoginView.as_view(authentication_form=UserAuthenticationForm)),
    path('bruker/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
