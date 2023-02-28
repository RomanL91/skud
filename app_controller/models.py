from django.db import models

from app_skud.models import Checkpoint, Staffs


# Здесь будут храниться все сущности, которые связанны
# с работой контроллера, например:
# -сущность контроллер
# -сущность события
# все, что может приходить от контроллера

CHOICES_CONTROLLER_ACTIVE = [
    ('1', 'active'),
    ('0', 'desactive'),
]

CHOICES_CONTROLLER_ONLINE = [
    ('1', 'online'),
    ('0', 'offline'),
]

CHOICES_CONTROLLER_MODE = [
    ('0', 'norma'),
    ('1', 'block'),
    ('2', 'free'),
    ('3', 'waiting for free passage'),
]


class Controller(models.Model):
    controller_type = models.CharField(verbose_name='Тип контроллера', max_length=10)
    serial_number = models.PositiveIntegerField(verbose_name='Серийный номер контроллера', unique=True)
    controller_activity = models.CharField(verbose_name='активность контроллера', max_length=1, choices=CHOICES_CONTROLLER_ACTIVE)
    controller_online = models.CharField(verbose_name='режим онлайн контроллера', max_length=1, choices=CHOICES_CONTROLLER_ONLINE, default='0')
    controller_mode = models.CharField(verbose_name='режим работы контроллера', max_length=1, choices=CHOICES_CONTROLLER_MODE)
    data_settings_zone = models.JSONField(editable=False, verbose_name='настройки зон контроллера', default=dict)
    other_data = models.JSONField(editable=False, verbose_name='остальные настройки', default=dict)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f'{self.controller_type} {self.serial_number}'


class Event(models.Model):
    event = models.PositiveIntegerField(verbose_name='событие')
    card = models.CharField(verbose_name='номер карты', max_length=15)
    time = models.CharField(verbose_name='время события', max_length=50)
    flag = models.PositiveIntegerField(verbose_name='флаг события')
    data_event = models.JSONField(verbose_name='дополнительная информация о событиии')
    controller = models.ForeignKey(Controller, on_delete=models.SET_NULL, null=True, blank=True)
    event_initiator = models.ForeignKey(Staffs, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.card} {self.event}'
