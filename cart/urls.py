from django.urls import path
from .views import (
    AddToCartAPIView,
    CartListAPIView,
    DecreaseCartAPIView,
    RemoveFromCartAPIView
)

urlpatterns = [
    path("", CartListAPIView.as_view()),
    path("<int:product_id>/add/", AddToCartAPIView.as_view()),
    path("<int:product_id>/decrease/", DecreaseCartAPIView.as_view()),
    path("<int:product_id>/remove/", RemoveFromCartAPIView.as_view()),
]

