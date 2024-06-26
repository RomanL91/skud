from datetime import date

from rest_framework import generics

from django.http import JsonResponse

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from app_skud.models import MonitorEvents, Checkpoint
from app_skud.serializers import MonitorEventsSerializer, PerimetrMonitorSerializer


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
        checkpoint = self.object.name_checkpoint
        monitor_filter_to_render = MonitorEvents.objects.filter(
            checkpoint = kwargs['pk']
        )
        context = {
            'monitor_filter_to_render': monitor_filter_to_render, 
            'pk_checkpoint': kwargs['pk'], 
            'checkpoint': checkpoint
        }

        return self.render_to_response(context)
    

class MonitorEventsApiView(generics.ListAPIView):
    queryset = MonitorEvents.objects.all()
    serializer_class = MonitorEventsSerializer

    def list(self, request, *args, **kwargs):
        today = date.today()
        queryset = self.filter_queryset(self.get_queryset().filter(checkpoint=kwargs['pk_checkpoint'])).filter(time_created__date=today)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


from app_observer.models import PerimeterMonitor

class PerimetrMonitorApiView(generics.ListAPIView):
    queryset = PerimeterMonitor.objects.all()
    serializer_class = PerimetrMonitorSerializer

    def list(self, request, *args, **kwargs):
        checkpoint_id = kwargs['pk_checkpoint'] 
        queryset = self.filter_queryset(queryset=self.queryset.filter(perimeter_gates=checkpoint_id))
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
