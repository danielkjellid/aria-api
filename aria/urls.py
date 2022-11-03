from django.contrib import admin
from django.urls import path

from aria.api.apis.internal.v1 import api_internal as api_v1_internal
from aria.api.apis.public.v1 import api as api_v1

urlpatterns = [
    path("alpha/", admin.site.urls),
    path("api/v1/", api_v1.urls),
    path("api/v1/internal/", api_v1_internal.urls),
]
