from .views import CheckoutAPIView,OrderDetailAPIView,CODOrderAPIView,MyOrdersAPIView,CancelOrderAPIView
from payments.views import CreateRazorpayOrderAPIView,VerifyRazorpayPaymentAPIView
from django.urls import path

urlpatterns = [
    path("checkout/", CheckoutAPIView.as_view()),
    path("<int:pk>/", OrderDetailAPIView.as_view()),
    path("razorpay/create/", CreateRazorpayOrderAPIView.as_view()),
    path("razorpay/verify/", VerifyRazorpayPaymentAPIView.as_view()),
    path("cod/", CODOrderAPIView.as_view()),
    path("my-orders/", MyOrdersAPIView.as_view()),
    path("cancel/", CancelOrderAPIView.as_view(), name="cancel-order"),
]
