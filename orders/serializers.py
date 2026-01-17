from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.URLField(source="product.image", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "product_image", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    billing = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "status",
            "created_at",
            "razorpay_payment_id",
            "items",
            "billing"
        ]

    def get_billing(self, obj):
        return {
            "billingName": obj.billing_name,
            "billingEmail": obj.billing_email,
            "billingPhone": obj.billing_phone,
            "billingAddress": obj.billing_address,
            "billingCity": obj.billing_city,
            "billingState": obj.billing_state,
            "billingZip": obj.billing_zip,
            "billingCountry": obj.billing_country,
        }

