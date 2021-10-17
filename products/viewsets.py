from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAdminUser

from core.permissions import HasUserOrGroupPermission

from products.models import Product
from products.serializers import ProductListByCategorySerializer, ProductListSerializer, ProductSerializer
from core.pagination import PageNumberSetPagination


class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    View for listing all products in application backend

    Returns list of products.
    """

    queryset = Product.objects.all().order_by('id')
    pagination_class = PageNumberSetPagination
    search_fields = ('name', 'supplier__name', 'search_keywords', 'status')
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'GET': ['has_products_list'],
        'POST': ['has_product_add'],
    }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer

        return ProductListSerializer


class ProductListByCategoryAPIView(generics.ListAPIView):
    """
    This viewset takes the category parameter given by the url and find related products
    """

    permission_classes = (AllowAny, )
    authentication_classes = ()
    serializer_class = ProductListByCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'supplier__name', 'category__name', 'materials__name', 'styles__name', 'search_keywords')

    def get_queryset(self):
        """
        Gets parameter in urls and filters the product model
        """

        category = self.kwargs['category']

        return Product.on_site.filter(
            category__parent__slug=category, 
            status=3
        ).distinct()


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    """
    Viewset for getting a specific product instance based on slug
    """

    permission_classes = (AllowAny, )
    authentication_classes = ()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.all()