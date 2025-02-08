from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DisasterNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_channel_name = "user_" + str(self.scope["user"].id)
        await self.channel_layer.group_add(self.user_channel_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user_channel_name = "user_" 
        await self.channel_layer.group_discard(user_channel_name, self.channel_name)


    async def receive(self, text_data):
        message_data = json.loads(text_data)
        message_type = message_data.get("type")
        if message_type == "disasterNotification":
            notification_message = message_data.get("message")
            await self.send(text_data=json.dumps({"response": notification_message}))
        else:
            pass


    async def disasterNotification(self, event):
        text_data = event["message"]
        if text_data:
            message_type = event["type"]
            if message_type == "disasterNotification":
                await self.send(text_data=json.dumps({"response": text_data}))


