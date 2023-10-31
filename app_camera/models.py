from django.db import models

from app_skud.models import Checkpoint
from app_controller.models import Controller

from app_skud.utils_to_microscope import (
    commands_RESTAPI_microscope, list_choise_camera,
    login, passw, URL_SDK, CONFIGEX_MICRPSCOPE)


response = commands_RESTAPI_microscope(
    url=URL_SDK, 
    login=login, 
    passw=passw, 
    method='get', 
    point=CONFIGEX_MICRPSCOPE
)

try:
    SELECT_CAMERA = list_choise_camera(list_id_camera_microscope=response['body_response'])
except:
    SELECT_CAMERA = (('', ''),)


class Camera(models.Model):
    SELECT_DIRECTIONS =(
        ("ВХОД", "ВХОД"),
        ("ВЫХОД", "ВЫХОД"),
    )
    name = models.CharField(verbose_name='Имя камеры', choices=SELECT_CAMERA, help_text='Выбирите камеру из списка', max_length=100)
    description = models.TextField(verbose_name='Описание', help_text='Краткое описание', blank=True)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, verbose_name='Проходная', help_text='Выбирите проходную, к которой будет привязана камера')
    direction = models.CharField(verbose_name='Направление', choices=SELECT_DIRECTIONS, help_text='Выирите направление, куда обращена камера', max_length=6)
    id_camera_microscope = models.CharField(max_length=100, blank=True, editable=False)
    other_data_camera = models.JSONField(editable=False, verbose_name='остальные настройки', default=dict)
    controllers = models.ManyToManyField(Controller, verbose_name='Контроллеры:', help_text='Выбирите контроллеры, связанные с этой камерой.')


    class Meta:
        verbose_name = 'Камера'
        verbose_name_plural = 'Камеры'
        constraints = (
            models.UniqueConstraint(
                fields=('checkpoint', 'direction', 'name'), 
                name='%(app_label)s_%(class)s_checkpoint_direct_name'
            ),
        )

    def __str__(self) -> str:
        return self.name
    

from django.db.models.signals import post_save
from django.dispatch import receiver
from app_camera.http_long import main
import asyncio
from multiprocessing import Process


def mainn(channel_id_macroscope):
        asyncio.run(main(channel_id_macroscope))


@receiver(post_save, sender=Camera)
def signal_to_observer(sender, instance, created, **kwargs):
    proc = Process(target=mainn, args=(instance.id_camera_microscope,), name=instance.id_camera_microscope)
    proc.start()
    Camera.objects.filter(pk=instance.pk).update(other_data_camera={'pid': proc.pid})
