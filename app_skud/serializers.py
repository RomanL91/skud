from rest_framework import serializers

from .models import (
    Staffs,
    Department,
    Position,
    AccessProfile,
    Checkpoint,
    MonitorEvents
)

from app_controller.functions_working_database import get_information_about_employee_to_send


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
    # department = DepartamentSerializer()
    # position = PositionSerializer()
    # access_profile = AccessProfileSerializer()
    class Meta:
        model = Staffs
        fields = (
            "id",
            "employee_photo",
            # "last_name",
            # "first_name",
            "patronymic",
            # "phone_number",
            "home_address",
            "car_number",
            "car_model",
            # "department",
            "position",
            "access_profile",
            # "pass_number",
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
    controller = ControllerSerializer()
    class Meta:
        model = MonitorEvents
        fields = (
            'operation_type',
            'time_created',
            'card',
            'controller',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            event = 'Доступ запрешен'
            if instance.data_monitor_events['granted']:
                event = 'Доступ разрешен'
            new_data = {
                "event_initiator": {
                    "last_name": instance.staff.split(' ')[0] if instance.staff != 'None' and instance.staff != None else ' --- ',
                    "first_name": instance.staff.split(' ')[1] if instance.staff != 'None' and instance.staff != None else ' --- ',
                    "patronymic": instance.staff.split(' ')[2] if instance.staff != 'None' and instance.staff != None else ' --- ',
                    "department": {"name_departament": instance.data_monitor_events['dep'] if instance.staff != 'None' else ' --- '},
                    "employee_photo": instance.data_monitor_events['photo']
                },
                "controller": {"checkpoint": {"description_checkpoint": str(instance.checkpoint)}},
                "time": instance.time_created,
                "flag": instance.data_monitor_events['direct'],
                "data_event": {"event": event if instance.card != 'Open Button' else instance.card},
                'late_status': instance.data_monitor_events['late_status'],
            }
        except Exception as e:
            print(f'[=WARNING=] The employee who initiated the event was not found in the database.')
            print(f'[=WARNING=] Event initiator pass number: {representation["card"]}.')
            print(f'[=WARNING=] Exception: {e}.')
            return representation
        representation['event'] = new_data
        return representation 


from app_observer.models import PerimeterMonitor

class PerimetrMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerimeterMonitor
        fields = (
            "perimeter_data",
        )
        