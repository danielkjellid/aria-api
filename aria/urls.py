from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/auth/", include("aria.core.urls")),
    path("api/", include("aria.users.urls")),
    path("api/", include("aria.kitchens.api.urls")),
    path("api/", include("aria.products.urls")),
    path("api/", include("aria.product_categorization.urls")),
    path("api/", include("aria.notes.urls")),
    path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
