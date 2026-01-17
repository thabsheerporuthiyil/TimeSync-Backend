from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.generics import RetrieveAPIView
from .serializers import OrderSerializer
from django.db.models import F

from cart.models import Cart
from .models import Order, OrderItem

class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        billing = request.data.get("billing")
        if not billing:
            return Response({"error": "Billing info missing"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        return Response({
            "amount": total_amount
        })


#order detail
class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

#confirm order
class CODOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        billing = request.data.get("billing")

        if not billing:
            return Response({"error": "Billing info missing"}, status=400)

        cart_items = Cart.objects.select_related("product").filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # Create Order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            payment_method="cod",
            status="confirmed", 
            billing_name=billing["name"],
            billing_email=billing["email"],
            billing_phone=billing["phone"],
            billing_address=billing["address"],
            billing_city=billing["city"],
            billing_state=billing["state"],
            billing_zip=billing["zip"],
            billing_country=billing["country"],
        )

        # Create Order Items + Reduce Stock
        for item in cart_items:
            product = item.product

            if product.stock < item.quantity:
                raise Exception(f"{product.name} is out of stock")

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item.quantity,
            )

            product.stock = F("stock") - item.quantity
            product.save()

        # Clear cart
        cart_items.delete()

        return Response({
            "success": True,
            "order_id": order.id
        })
    

class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        order = Order.objects.select_for_update().get(
            id=request.data.get("order_id"),
            user=request.user
        )

        if order.status in ["cancelled", "delivered"]:
            return Response(
                {"error": "Order cannot be cancelled"},
                status=400
            )


        if order.payment_method == "razorpay":
            return Response(
                {"error": "Paid orders via Razorpay cannot be cancelled online. Please contact support."},
                status=400
            )


        if order.status in ["confirmed", "pending"]:
            for item in order.items.select_related("product"):
                product = item.product
                product.stock = F("stock") + item.quantity
                product.save()

        order.status = "cancelled"
        order.save()

        return Response({"success": True, "message": "Order cancelled successfully"})

