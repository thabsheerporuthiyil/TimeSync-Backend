from django.urls import path
from .views import NotificationListAPIView, MarkNotificationReadAPIView,AdminSendNotificationView

urlpatterns = [
    path("", NotificationListAPIView.as_view()),
    path("<int:pk>/read/", MarkNotificationReadAPIView.as_view()),
    path("admin/send/", AdminSendNotificationView.as_view()),
]
