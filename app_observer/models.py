from django.db import models

from app_skud.models import Checkpoint


class PerimeterMonitor(models.Model):
    name = models.CharField(verbose_name='Имя периметра', help_text='Укажите имя периметра для наблюдения', max_length=100)
    description = models.TextField(verbose_name='Описание', help_text='Краткое описание', blank=True)
    perimeter_gates = models.ManyToManyField(Checkpoint, verbose_name='Проходные периметра', help_text='Укажите проходные данного периметра')
    perimeter_counter = models.IntegerField(verbose_name='Счётчик периметра', help_text='Показывает сколько людей в периметре')
    perimeter_data = models.JSONField(editable=False, verbose_name='Хранилище экземпляра', default=dict)
    
    class Meta:
        verbose_name = 'Периметр наблюдения'
        verbose_name_plural = 'Периметр наблюдения'
       

    def __str__(self) -> str:
        return self.name
    