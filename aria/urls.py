from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from aria.api.apis.internal.v1 import api_internal as api_v1_internal
from aria.api.apis.public.v1 import api as api_v1

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/v1/", api_v1.urls),
    path("api/v1/internal/", api_v1_internal.urls),
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)  # type: ignore
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)  # type: ignore # pylint: disable=line-too-long
