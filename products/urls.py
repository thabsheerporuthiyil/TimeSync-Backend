from .views import ProductListAPIView,ProductDetailAPIView
from django.urls import path

urlpatterns = [
    path('products/',ProductListAPIView.as_view()),
    path("products/<int:id>/", ProductDetailAPIView.as_view()),
]