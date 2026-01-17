from rest_framework.views import APIView
from .serializers import NotificationSerializer,AdminSendNotificationSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import Notification
from rest_framework.response import Response
from rest_framework import status
from .utils import send_notification


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"status": "read"})


class AdminSendNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminSendNotificationSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.context["target_user"]
        title = serializer.validated_data["title"]
        message = serializer.validated_data["message"]

        send_notification(user, title, message)

        return Response(
            {"detail": "Notification sent successfully"},
            status=status.HTTP_201_CREATED,
        )