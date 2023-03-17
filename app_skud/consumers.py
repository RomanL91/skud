import json
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import channels


class MySyncConsumer(SyncConsumer):
    __instanse = None

    def __new__(cls, *args, **kwargs):
        if cls.__instanse is None:
            cls.__instanse = super(SyncConsumer, cls).__new__(cls)
        return cls.__instanse

    def websocket_connect(self, event):
        print(f"Websocket Connected...")
        self.send({"type": "websocket.accept"})

    def websocket_receive(self, event):
        print(f"Websocket Received...")
        self.send({"type": "websocket.send", "text": event})
           
    def websocket_disconnect(self, event):
        print(f"Websocket Disconnect...")
        raise StopConsumer()


class MyAsyncConsumer(AsyncConsumer):
    __instanse = None

    def __new__(cls, *args, **kwargs):
        if cls.__instanse is None:
            cls.__instanse = super().__new__(cls)
        return cls.__instanse

    async def websocket_connect(self, event):
        print(f"Websocket Connected...")
        self.room_group_name = 'ALL'
        self.channel_name = 'mon'
        await self.send({"type": "websocket.accept", "text": str(event)})
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)


    async def websocket_receive(self, event):
        print(f"Websocket Received...")
        # await self.send({"type": "websocket.send", "text": event})
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": event}
        )

    async def chat_message(self, event):
        print(f'event --->>> {event}')
        # await self.channel_layer.group_add("ALL", 'mon')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": event}))
        # await self.channel_layer.group_send(
            # 'ALL', {"type": "chat_message", "message": event}
        # )
       


    async def websocket_disconnect(self, event):
        print(f"Websocket Disconnect...")
        raise StopConsumer()
    

class ChatConsumer(AsyncWebsocketConsumer):
    groups = ['ALL']
    __instanse = None

    def __new__(cls, *args, **kwargs):
        if cls.__instanse is None:
            cls.__instanse = super().__new__(cls)
        return cls.__instanse
    
    async def connect(self):
        self.room_group_name = 'ALL'
        self.channel_name = 'mon'

        print(f'channel_layer --->>> {self.channel_layer}')
        print(f'connect_room --->>> {self.room_group_name}')
        print(f'connect_channel_name --->>> {self.channel_name}')

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        print(f'--->>> {self.channel_layer.__dict__}')

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # message = text_data_json["message"]

        print(f'text_data ---->>> {text_data}')
        print(f'text_data_json ---->>> {text_data_json}')
        print(f'self.channel_layer ---->>> {self.channel_layer}')
        print(f'---->>> {self.room_group_name}')

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": text_data_json}
        )

    # Receive message from room group
    async def chat_message(self, event):
        print(f'event --->>> {event}')
        await self.channel_layer.group_add("ALL", 'mon')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": event}))
        # await self.channel_layer.group_send(
        #     'ALL', {"type": "chat_message", "message": event}
        # )

    async def forward_group_message(self, event):
        await self.send(json.dumps(event['message'], default=str))








import channels.layers
class BotConsumer(AsyncJsonWebsocketConsumer):
    __instanse = None

    def __new__(cls, *args, **kwargs):
        if cls.__instanse is None:
            cls.__instanse = super().__new__(cls)
        return cls.__instanse
    
    async def connect(self):
        print(f'channel_layer --->>> {self.channel_layer}')
        # print(f'connect_room --->>> {self.room_group_name}')
        # print(f'connect_channel_name --->>> {self.channel_name}')
        
        await self.accept()
        await self.channel_layer.group_add("bot",self.channel_name)
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("bot",self.channel_name)

    async def receive(self, text_data):
        print('BotConsumer recive')
        await self.channel_layer.group_send("client",{
            "type":"recv",
            "message":text_data
        })

        print("Data sent to group")



class WebClientConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(f'channel_layer --->>> {self.channel_layer}')

        await self.accept()
        await self.channel_layer.group_add("client",self.channel_name)

    async def recv(self,event):
        print("Consumer received smthing from channels")
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("client",self.channel_name)

    async def receive(self, text_data):
        print("Smthing received")