from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_patterns = [
    path("auth/", include("aria.auth.urls")),
    path("users/", include("aria.users.urls")),
    path(
        "v2/categories/", include("aria.categories.urls")
    ),  # TODO: remove v2 from path when migration is done
]

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/", include("aria.kitchens.urls")),
    path("api/", include("aria.products.urls")),
    path("api/", include("aria.product_categorization.urls")),
    path("api/", include("aria.notes.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(api_patterns)),
]


if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)
