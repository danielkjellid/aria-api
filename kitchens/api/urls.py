from django.urls import path
from kitchens.api.viewsets import (KitchenListAPIView, KitchenRetrieveAPIView)

urlpatterns = [
    # endpoint for geting list of all kitchens
    path('kitchens/', KitchenListAPIView.as_view(), name='kitchen_list'),
    # endpoint for getting a single kitchen instance
    path('kitchens/<slug:slug>/', KitchenRetrieveAPIView.as_view(), name='kitchen_detail'),
]