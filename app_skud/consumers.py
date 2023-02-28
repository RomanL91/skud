from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer


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
        await self.send({"type": "websocket.accept", "text": str(event)})

    async def websocket_receive(self, event):
        print(f"Websocket Received...")
        await self.send({"type": "websocket.send", "text": event})

    async def websocket_disconnect(self, event):
        print(f"Websocket Disconnect...")
        raise StopConsumer()
