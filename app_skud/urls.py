from django.urls import path

from app_skud.view import MonitorEventsListView


urlpatterns = [
    path("", MonitorEventsListView.as_view(), name="monitor_events"),
]