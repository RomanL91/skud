from django.urls import path

from .views import (
    controller_request_receiver_gateway,
    ControllersListView,
    ControllerDetailView,
    ControllerUpdateView,
    ControllerDeleteView,
)


urlpatterns = [
    path("", controller_request_receiver_gateway, name="gate"),
    path("controllers_list/", ControllersListView.as_view(), name="controllers_list"),
    path("controller/<int:pk>/", ControllerDetailView.as_view(), name="controller"),
    path("controller/<int:pk>/edit/", ControllerUpdateView.as_view(), name="controller_edit",),
    path("controller/<int:pk>/delete/", ControllerDeleteView.as_view(), name="controller_delete",),
]
