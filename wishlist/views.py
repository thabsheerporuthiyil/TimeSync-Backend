from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wishlist
from products.models import Product
from .serializers import WishlistSerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework import status


class ToggleWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        )

        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({"status": "removed"})
        else:
            Wishlist.objects.create(
                user=request.user,
                product_id=product_id
            )
            return Response({"status": "added"})
        

class WishlistListCreateAPIView(ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WishlistDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

