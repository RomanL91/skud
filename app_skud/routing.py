from django.urls import path
from . import consumers
# from app_controller.functions_working_database import MyAsyncConsumer


websocket_urlpatterns = [
    path("ws/sc/", consumers.MySyncConsumer.as_asgi()),
    path("ws/ac/", consumers.MyAsyncConsumer.as_asgi()),
]
