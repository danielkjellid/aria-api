from django.contrib import admin
from django.urls import include, path, re_path

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('alpha/', admin.site.urls),
    path('api/auth/', include('core.urls')),
    path('api/', include('users.api.urls')),
    path('api/', include('inventory.api.urls')),
    path('api/', include('kitchens.api.urls')),
    path('api/', include('utils.api.urls')),
    path('api/', include('products.urls')),
    path('api-auth/', include('rest_framework.urls')),
] 

if settings.DEBUG:
    urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
