import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order,OrderItem
import hmac, hashlib
from cart.models import Cart
from django.db.models import F
from django.db import transaction

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

class CreateRazorpayOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        amount = int(total_amount * 100)

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return Response({
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID
        })

    

class VerifyRazorpayPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data = request.data
        user = request.user

        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != data["razorpay_signature"]:
            return Response({"error": "Payment verification failed"}, status=400)

        cart_items = Cart.objects.select_related("product").filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        billing = data["billing"]

        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            status="paid",
            payment_method="razorpay",
            razorpay_order_id=data["razorpay_order_id"],
            razorpay_payment_id=data["razorpay_payment_id"],
            razorpay_signature=data["razorpay_signature"],
            billing_name=billing["name"],
            billing_email=billing["email"],
            billing_phone=billing["phone"],
            billing_address=billing["address"],
            billing_city=billing["city"],
            billing_state=billing["state"],
            billing_zip=billing["zip"],
            billing_country=billing["country"],
        )

        for item in cart_items:
            if item.product.stock < item.quantity:
                raise Exception("Stock issue")

            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

            item.product.stock = F("stock") - item.quantity
            item.product.save()

        cart_items.delete()

        return Response({"success": True, "order_id": order.id})
