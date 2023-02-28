from rest_framework import serializers

from .models import Controller
from app_skud.serializers import CheckpointSerializer


class ControllerSerializer(serializers.ModelSerializer):
    checkpoint = CheckpointSerializer()
    class Meta:
        model = Controller
        fields = (
            'id',
            'controller_type',
            'serial_number',
            'controller_activity',
            'controller_online',
            'controller_mode',
            'data_settings_zone',
            'other_data',
            'checkpoint',
        )