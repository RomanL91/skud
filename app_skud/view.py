from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from app_skud.models import MonitorEvents, Checkpoint


class MonitorEventsListView(ListView):
    model = MonitorEvents
    context_object_name = 'events'


class CheckpointsListView(ListView):
    model = Checkpoint
    context_object_name = 'checkpoints'


class CheckpointDetailView(DetailView):
    model = Checkpoint

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        monitor_filter_to_render = MonitorEvents.objects.filter(
            checkpoint = kwargs['pk']
        )
        context = {'monitor_filter_to_render': monitor_filter_to_render}

        return self.render_to_response(context)
