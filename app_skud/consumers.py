import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class WebClientConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("client",self.channel_name)

    async def recv(self,event):
        print("Consumer received smthing from channels")
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("client",self.channel_name)

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"event": text_data["text_data"]})) # WORK!!
        