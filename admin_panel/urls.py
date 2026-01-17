from django.urls import path
from .views import AdminDashboardAPIView,StockSummaryAPIView,BrandSalesAPIView,BrandProductCountAPIView,AdminUserListAPIView,ToggleBlockUserAPIView,ProductListCreateAPIView,ProductRetrieveUpdateDeleteAPIView,AdminOrderListView,AdminOrderStatsAPIView,AdminOrderStatusUpdateAPIView,AdminRevenueAPIView

urlpatterns = [
    path("dashboard/", AdminDashboardAPIView.as_view()),
    path("stock-summary/", StockSummaryAPIView.as_view()),
    path("brand-sales/", BrandSalesAPIView.as_view()),
    path("brand-count/", BrandProductCountAPIView.as_view()),
    path("revenue/", AdminRevenueAPIView.as_view()),
    path("users/", AdminUserListAPIView.as_view()),
    path("users/<int:user_id>/toggle-block/", ToggleBlockUserAPIView.as_view()),
    path("products/", ProductListCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductRetrieveUpdateDeleteAPIView.as_view()),
    path("orders/", AdminOrderListView.as_view()),
    path("orders/stats/", AdminOrderStatsAPIView.as_view()),
    path("orders/<int:order_id>/status/", AdminOrderStatusUpdateAPIView.as_view()),
]
