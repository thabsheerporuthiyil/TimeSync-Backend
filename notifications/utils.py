from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def send_notification(user, title, message):
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "data": {
                "id": notification.id,
                "title": title,
                "message": message,
                "is_read": notification.is_read,
                "created_at": str(notification.created_at),
            }
        }
    )
