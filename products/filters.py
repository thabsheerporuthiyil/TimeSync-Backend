from django_filters import rest_framework as filters
from .models import Product

# request comes with query parameters -> database filters
class ProductFilter(filters.FilterSet):
    category__filter_key = filters.CharFilter(
        field_name="category__filter_key",
        lookup_expr="iexact"
    )

    brand__name = filters.CharFilter(
        field_name="brand__name",
        lookup_expr="iexact"
    )

    price__lt = filters.NumberFilter(field_name="price", lookup_expr="lt")
    price__gt = filters.NumberFilter(field_name="price", lookup_expr="gt")
    price__lte = filters.NumberFilter(field_name="price", lookup_expr="lte")
    price__gte = filters.NumberFilter(field_name="price", lookup_expr="gte")

    class Meta:
        model = Product
        fields = [
            "category__filter_key",
            "brand__name",
            "price",
        ]
