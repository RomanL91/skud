from django.views.generic.list import ListView

from app_skud.models import MonitorEvents


class MonitorEventsListView(ListView):
    model = MonitorEvents
    context_object_name = 'events'