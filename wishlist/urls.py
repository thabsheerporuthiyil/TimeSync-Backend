from django.urls import path
from .views import ToggleWishlistAPIView, WishlistListCreateAPIView,WishlistDeleteAPIView

urlpatterns = [
    path("", WishlistListCreateAPIView.as_view()),
    path("<int:product_id>/", WishlistDeleteAPIView.as_view()), 
    path("<int:product_id>/toggle/", ToggleWishlistAPIView.as_view()),
]