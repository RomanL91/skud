from django.contrib import admin

from app_camera.models import Camera
from app_camera.forms import CameraModelForm

from app_skud.utils_to_microscope import (
    URL_SDK, CONFIGEX_MICRPSCOPE, login, passw,
    commands_RESTAPI_microscope, get_name_id_camera_to_name_camera)


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
        obj.id_camera_microscope = id_camera_microscope[form.data['name']]
        obj.save()