from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)
    category_filter_key = serializers.CharField(source="category.filter_key", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "image",
            "stock",
            "brand_name",
            "category_title",
            "category_filter_key",
        ]

