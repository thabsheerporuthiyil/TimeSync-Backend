from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from products.models import Product
from .serializers import CartSerializer
from django.db import transaction


class CartListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.filter(user=request.user).select_related('product')
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data)

class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"quantity": 0}
        )

        if cart_item.quantity + 1 > product.stock:
            return Response(
                {"error": "Only limited stock available"},
                status=400
            )

        cart_item.quantity += 1
        cart_item.save()

        return Response({"status": "added"})


class DecreaseCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        cart_item = Cart.objects.filter(
            user=request.user,
            product_id=product_id
        ).first()

        if not cart_item:
            return Response(status=404)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        return Response({"status": "updated"})

class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        Cart.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
