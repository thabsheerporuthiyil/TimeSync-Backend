from .models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title="Order Placed",
            message=f"Your order #{instance.id} has been placed successfully"
        )
        # We generally don't need to send the WS message here manually anymore
        # because the Notification.post_save signal below will handle it.

@receiver(post_save, sender=Notification)
def send_websocket_notification(sender, instance, created, **kwargs):
    if created:
        print(f"DEBUG: Notification created for User {instance.user.id}: {instance.title}")
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.user.id}"
        
        try:
            print(f"DEBUG: Sending to group {group_name}")
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "data": {
                        "id": instance.id,
                        "title": instance.title,
                        "message": instance.message,
                        "is_read": instance.is_read,
                        "created_at": instance.created_at.isoformat(),
                    }
                }
            )
            print("DEBUG: Signal sent to channel layer")
        except Exception as e:
            print(f"DEBUG: Failed to send WebSocket notification: {e}")

