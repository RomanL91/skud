import psutil

from time import sleep

from django.contrib import admin

from app_camera.models import Camera
from app_camera.forms import CameraModelForm

from app_skud.utils_to_microscope import (
    URL_SDK, CONFIGEX_MICRPSCOPE, login, passw,
    commands_RESTAPI_microscope, get_name_id_camera_to_name_camera)

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
        obj.save()


    def delete_model(self, request, obj):
        try:
            pid = obj.other_data_camera['pid']
            p = psutil.Process(pid=pid)
            p.kill()
        except Exception as e:
            print(f'e --->>> {e}')
        obj.delete()









        # try:
        #     parent_proc = multiprocessing.parent_process()
        #     print(f'parent_proc ---------->> {parent_proc}')

        #     list_proc = multiprocessing.active_children()
        #     print(f'list_proc ---------->> {list_proc}')

        #     for proc in list_proc:
        #         print(f'proc.name ----->>> {proc.name}')
        #         print(f'obj.id_camera_microscope ----->>> {obj.id_camera_microscope}')
        #         if proc.name == obj.id_camera_microscope:
        #             print('KILL PROC')
        #             proc.kill()
        #             sleep(0.1)
        #     obj.delete()
        # except Exception as e:
        #     print(f'e --->>> {e}')
