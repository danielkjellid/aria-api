from django.http import HttpRequest, HttpResponse
import json
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status
from rest_framework.response import Response
from aria.categories.selectors import categories_navigation_active_list


from aria.core.serializers import inline_serializer
from aria.categories.models import Category


class CategoryNavigationListAPI(APIView):
    """
    [PUBLIC] Endpoint to fetch categories used for
    routing in the frontend navbar.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.SlugField()
        children = serializers.SerializerMethodField()

        class ChildSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
            slug = serializers.SlugField()
            ordering = serializers.IntegerField()

        def get_children(self, parent):

            # Check if cached children exist. If not cached, filter
            # children to get active, as it gets all children by default.
            if hasattr(parent, "_cached_children"):
                children = parent.get_children()
            else:
                children = parent.get_children().active()

            return self.ChildSerializer(children, many=True).data

    def get(self, request: HttpRequest) -> HttpResponse:
        categories = categories_navigation_active_list()
        serializer = self.OutputSerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListAPI(APIView):
    pass


class CategoryDetailAPI(APIView):
    pass


class CategoryProductsListAPI(APIView):
    pass
