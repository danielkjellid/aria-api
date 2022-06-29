from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from aria.api.api import api as endpoints

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/", endpoints.urls),
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)  # type: ignore
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)  # type: ignore # pylint: disable=line-too-long
