from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from aria.api.api import api as endpoints

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", endpoints.urls),
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)
