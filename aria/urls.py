from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from aria.api.apis.internal_v1 import api_internal as internal_endpoints
from aria.api.apis.public_v1 import api_public as public_endpoints

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/v1/", public_endpoints.urls),
    path("api/v1/internal/", internal_endpoints.urls),
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)  # type: ignore
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)  # type: ignore # pylint: disable=line-too-long
