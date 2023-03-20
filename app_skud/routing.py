from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'live/webclient', consumers.WebClientConsumer.as_asgi()), 
]
