from django.db import models
from django.conf import settings


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("confirmed", "Confirmed (COD)"),
            ("paid", "Paid"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
            ("failed", "Failed"),
        ],
        default="pending", db_index=True
    )

    PAYMENT_CHOICES = (
        ("cod", "Cash On Delivery"),
        ("razorpay", "Razorpay"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="cod"
    )

    billing_name = models.CharField(max_length=100, null=True, blank=True)
    billing_email = models.EmailField(null=True, blank=True)
    billing_phone = models.CharField(max_length=20, null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    billing_city = models.CharField(max_length=50, null=True, blank=True)
    billing_state = models.CharField(max_length=50, null=True, blank=True)
    billing_zip = models.CharField(max_length=20, null=True, blank=True)
    billing_country = models.CharField(max_length=50, null=True, blank=True)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} x {self.quantity}"
