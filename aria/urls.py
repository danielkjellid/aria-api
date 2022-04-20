from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from aria.api.endpoints import endpoints

api_patterns = [
    path("auth/", include("aria.auth.urls")),
    path("categories/", include("aria.categories.urls")),
    path("products/", include("aria.products.urls")),
    path("users/", include("aria.users.urls")),
]

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/", include("aria.kitchens.urls")),
    path("api/", include("aria.products.urls")),
    path("api/", include("aria.notes.urls")),
    path("api/suppliers/", include("aria.suppliers.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(api_patterns)),
    path("test/", endpoints.urls)
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)
