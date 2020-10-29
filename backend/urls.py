from django.contrib import admin
from django.urls import include, path, re_path

from django.conf.urls.static import static
from backend import settings

urlpatterns = [
    path('alpha/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/', include('users.api.urls')),
    path('api/', include('inventory.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
