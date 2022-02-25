from django.urls import path

from aria.suppliers.viewsets.public import SupplierListAPI

internal_patterns = []

public_patterns = [path("", SupplierListAPI.as_view(), name="suppliers-list")]

urlpatterns = internal_patterns + public_patterns
