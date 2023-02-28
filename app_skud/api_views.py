from rest_framework import viewsets
from rest_framework import mixins


from .models import (
    Staffs,
    Department,
    Position,
    Checkpoint,
    AccessProfile,
    MonitorCheckAccess,
)
from .serializers import (
    StaffSerializer,
    StaffSerializer_,
    DepartamentSerializer,
    PositionSerializer,
    CheckpointSerializer,
    AccessProfileSerializer,
    AccessProfileSerializer_,
    MonitorCheckAccessSerializer,
)


class StaffViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Staffs.objects.all()
    serializer_classes = {
        "list": StaffSerializer_,
        "retrieve": StaffSerializer_,
        # Тут можно поиграться с настройками !!!!!
        # "retrieve": StaffSerializer_,
        # 'partial_update': StaffSerializer,
        # 'put': StaffSerializer_,
        # 'create': StaffSerializer,
        # 'update': StaffSerializer,
    }

    def get_serializer_class(self):
        # Тут можно поиграться с настройками !!!!!
        # print(f'action -->> {self.action}')
        return self.serializer_classes.get(self.action, StaffSerializer)


class DepartamentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartamentSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class CheckpointsViewSet(viewsets.ModelViewSet):
    queryset = Checkpoint.objects.all()
    serializer_class = CheckpointSerializer


class AccessProfileViewSet(viewsets.ModelViewSet):
    queryset = AccessProfile.objects.all()
    serializer_classes = {
        "list": AccessProfileSerializer,
        "retrieve": AccessProfileSerializer,
        # Тут можно поиграться с настройками !!!!!
        # "retrieve": StaffSerializer_,
        # 'partial_update': StaffSerializer,
        # 'put': StaffSerializer_,
        # 'create': StaffSerializer,
        # 'update': StaffSerializer,
    }

    def get_serializer_class(self):
        # Тут можно поиграться с настройками !!!!!
        # print(f'action -->> {self.action}')
        return self.serializer_classes.get(self.action, AccessProfileSerializer_)


class MonitorCheckAccessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonitorCheckAccess.objects.all()
    serializer_class = MonitorCheckAccessSerializer
