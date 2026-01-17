import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = None
        user = self.scope["user"]

        if user.is_anonymous:
            print("DEBUG: Consumer rejected anonymous user")
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            try:
                print(f"DEBUG: User {user.id} connecting. Adding to group {self.group_name}")
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                print(f"DEBUG: Added to group {self.group_name} successfully")
                await self.accept()
            except Exception as e:
                print(f"DEBUG: Error in consumer connect: {e}")
                await self.close()

    async def disconnect(self, close_code):
        if self.group_name:
            print(f"DEBUG: User disconnected. Removing from group {self.group_name}")
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        print(f"DEBUG: WebSocket sending message: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))

