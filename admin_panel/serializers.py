from rest_framework import serializers
from accounts.models import User
from products.models import Product
from orders.models import Order
from orders.serializers import OrderItemSerializer

class AdminUserSerializer(serializers.ModelSerializer):
    cart_count = serializers.IntegerField(read_only=True)
    wishlist_count = serializers.IntegerField(read_only=True)
    orders_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "role",
            "is_active",
            "cart_count",
            "wishlist_count",
            "orders_count",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "image",
            "stock",
            "brand",
            "category",
        ]


class ProductReadSerializer(serializers.ModelSerializer):
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


class AdminOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    paymentMethod = serializers.CharField(source="payment_method")
    ordered_date = serializers.DateTimeField(
        source="created_at",
        format="%d %b %Y, %I:%M %p",
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user_name",
            "user_email",
            "total_amount",
            "status",
            "paymentMethod",
            "ordered_date",
            "items",
        ]
