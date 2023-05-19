from django.db import models

from app_skud.models import Checkpoint


class Camera(models.Model):
    name = models.CharField(verbose_name='Имя камеры', help_text='Выбирите камера из списка', max_length=100)
    description = models.TextField(verbose_name='Описание', help_text='Краткое описание', blank=True)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, verbose_name='Проходная', help_text='Выбирите проходную, к которой будет привязана камера')
    direction = models.CharField(verbose_name='Направление', help_text='Выирите направление, куда обращена камера', max_length=6)
    id_camera_microscope = models.CharField(max_length=100)
    other_data_camera = models.JSONField(editable=False, verbose_name='остальные настройки', default=dict)

    class Meta:
        verbose_name = 'Камера'
        verbose_name_plural = 'Камеры'
        constraints = (
            models.UniqueConstraint(
                fields=('checkpoint', 'direction', 'name'), 
                name='app_camera_camera'
            ),
        )

    def __str__(self) -> str:
        return self.name