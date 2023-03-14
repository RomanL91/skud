from django.urls import path

from app_skud.view import MonitorEventsListView
from app_skud.f_export_from_DB import import_data_from_database


urlpatterns = [
    path("", MonitorEventsListView.as_view(), name="monitor_events"),
    path("exprort_data", import_data_from_database, name="exprort_data"),
]