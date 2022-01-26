from django.urls import path

from aria.categories.viewsets.public import CategoryNavigationListAPI

internal_patterns = []

public_patterns = [
    path(
        "navigation/",
        CategoryNavigationListAPI.as_view(),
        name="categories-navigation-list",
    ),
]

urlpatterns = internal_patterns + public_patterns
