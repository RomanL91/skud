from django.urls import path

from .views import (
    controller_request_receiver_gateway,
)


urlpatterns = [
    path("", controller_request_receiver_gateway, name="gate"),
]
