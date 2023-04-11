from rest_framework import serializers

from .models import (
    Staffs,
    Department,
    Position,
    AccessProfile,
    Checkpoint,
    MonitorEvents
)


class DepartamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            "id",
            "name_departament",
            "abbreviation",
            "data_departament",
        )


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = (
            "id",
            "name_position",
            "data_position",
        )


class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint
        fields = (
            "id",
            "name_checkpoint",
            "description_checkpoint",
            "data_checkpoint",
        )


class AccessProfileSerializer(serializers.ModelSerializer):
    checkpoints = CheckpointSerializer(many=True)

    class Meta:
        model = AccessProfile
        fields = (
            "id",
            "name_access_profile",
            "description_access_profile",
            "checkpoints",
        )


class AccessProfileSerializer_(serializers.ModelSerializer):
    # checkpoints = CheckpointSerializer(many=True)
    class Meta:
        model = AccessProfile
        fields = (
            "id",
            "name_access_profile",
            "description_access_profile",
            "checkpoints",
        )


class StaffSerializer(serializers.ModelSerializer):
    department = DepartamentSerializer()
    # position = PositionSerializer()
    # access_profile = AccessProfileSerializer()
    class Meta:
        model = Staffs
        fields = (
            "id",
            "employee_photo",
            "last_name",
            "first_name",
            "patronymic",
            "phone_number",
            "home_address",
            "car_number",
            "car_model",
            "department",
            "position",
            "access_profile",
            "pass_number",
            "data_staffs",
        )


class StaffSerializer_(serializers.ModelSerializer):
    department = DepartamentSerializer()
    position = PositionSerializer()
    access_profile = AccessProfileSerializer()

    class Meta:
        model = Staffs
        fields = (
            "id",
            "employee_photo",
            "last_name",
            "first_name",
            "patronymic",
            "phone_number",
            "home_address",
            "car_number",
            "car_model",
            "department",
            "position",
            "access_profile",
            "pass_number",
            "data_staffs",
        )

from app_controller.serializers import ControllerSerializer

class MonitorEventsSerializer(serializers.ModelSerializer):
    # staff = StaffSerializer()
    controller = ControllerSerializer()
    class Meta:
        model = MonitorEvents
        fields = (
            'operation_type',
            'time_created',
            'card',
            'staff',
            'controller',
            'checkpoint',
            'granted',
            'event',
            'flag',
            'data_monitor_events',
        )
        