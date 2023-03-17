from django.urls import path, re_path
from . import consumers


websocket_urlpatterns = [
    path("ws/sc/", consumers.MySyncConsumer.as_asgi()),
    path("ws/ac/", consumers.MyAsyncConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<checkpoint>\w+)/$", consumers.ChatConsumer.as_asgi()),
    # path("ws/chat/", consumers.ChatConsumer.as_asgi()),
    re_path(r'live/bot', consumers.BotConsumer.as_asgi()),
    re_path(r'live/webclient', consumers.WebClientConsumer.as_asgi()), 
]
