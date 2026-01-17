from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "page": self.page.number,
            "page_size": self.page.paginator.per_page,
            "total_pages": self.page.paginator.num_pages,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })

class ProductListAPIView(ListAPIView):
    queryset = (
        Product.objects
        .select_related("brand", "category")
        .only(
            "id", "name", "price", "stock", "image",
            "brand__name",
            "category__filter_key",
            "category__title",
        )
    )

    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = ProductFilter

    search_fields = [
        "name__icontains",
        "brand__name__icontains",
        "category__filter_key__icontains",
    ]


class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related("brand", "category")
    serializer_class = ProductSerializer
    lookup_field = "id"