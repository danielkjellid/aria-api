from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from django_registration.backends.one_step.views import RegistrationView

from core.views import IndexTemplateView
from users.forms import UserAuthenticationForm, UserRegistrationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bruker/registrer/', RegistrationView.as_view(form_class=UserRegistrationForm, success_url='/'), name='user-registration'),
    path('bruker/logg-inn/', auth_views.LoginView.as_view(authentication_form=UserAuthenticationForm), name='user-login'),
    path('api/', include('users.api.urls')),
    path('api/', include('inventory.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^.*$', IndexTemplateView.as_view(), name='entry-point')
]
