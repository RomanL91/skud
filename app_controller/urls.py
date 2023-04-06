from django.urls import path

from .views import (
    controller_request_receiver_gateway,
    del_card_from_controller,
    add_card
)


urlpatterns = [
    path("", controller_request_receiver_gateway, name="gate"),
    path("del_cads/<str:cards_number>/from_<str:serial_number>/", del_card_from_controller, name="del_card_from_controller"),
    path("add_card/in_<str:serial_number>/", add_card, name="add_card"),
]
