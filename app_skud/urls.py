from django.urls import path, re_path

from app_skud.view import MonitorEventsListView, CheckpointsListView, CheckpointDetailView


urlpatterns = [
    # path("", MonitorEventsListView.as_view(), name="monitor_events"),
    path("selects_monitors/", CheckpointsListView.as_view(), name="selects_monitors"),
    re_path(r'^selects_monitors/(?P<pk>\d+)$', CheckpointDetailView.as_view(), name="monitors_detail_checkpoint"),
]