from django.contrib import admin

from app_camera.models import Camera
from app_camera.forms import CameraModelForm
from app_camera.tasks import http_long_macroscope

from app_skud.utils_to_microscope import (
    URL_SDK, CONFIGEX_MICRPSCOPE, login, passw,
    commands_RESTAPI_microscope, get_name_id_camera_to_name_camera)

from core.celery import app
from django_celery_beat.admin import (
    PeriodicTask, SolarSchedule, 
    ClockedSchedule, CrontabSchedule,
    IntervalSchedule, 
)


admin.site.unregister(PeriodicTask)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(SolarSchedule)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    form = CameraModelForm
    list_display = [
        'name',
        'description',
        'checkpoint',
        'direction',
        'id_camera_microscope',
        'other_data_camera',
    ]

    def save_model(self, request, obj, form, change):
        response = commands_RESTAPI_microscope(
            url=URL_SDK,
            login=login, passw=passw,
            method='get', point=CONFIGEX_MICRPSCOPE
        )
        id_camera_microscope = get_name_id_camera_to_name_camera(
            name_camera=form.data['name'],
            list_camera_from_microscope=response['body_response']
        )
        id_camera_microscope = id_camera_microscope[form.data['name']]
        obj.id_camera_microscope = id_camera_microscope
        id_process = str(http_long_macroscope.delay(id_camera_microscope))
        obj.other_data_camera = {id_camera_microscope: id_process}
        obj.save()


    def delete_model(self, request, obj):
        try:
            id_process = obj.other_data_camera[obj.id_camera_microscope]
        except KeyError:
            id_process = None
        obj.delete()
        app.control.revoke(id_process, terminate=True)
