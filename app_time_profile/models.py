from django.db import models


help_text = 'Пожалуйста, используте установленный формат: ЧЧ:ММ'

class TimeProfile(models.Model):
    name_time_profile = models.CharField(verbose_name='Название профиля доступа', unique=True, max_length= 150, help_text='Поле для ввода названия профиля доступа по времени')
    descriptions = models.TextField(verbose_name='Описание профиля доступа', blank=True, help_text='Поле для ввода описания данного профиля доступа по времени')
    monday =  models.TimeField(verbose_name='Понедельник', blank=True, null=True, help_text=help_text)
    tuesday =  models.TimeField(verbose_name='Вторник', blank=True, null=True, help_text=help_text)
    wednesday = models.TimeField(verbose_name='Среда', blank=True, null=True, help_text=help_text)
    thursday = models.TimeField(verbose_name='Четверг', blank=True, null=True, help_text=help_text)
    friday = models.TimeField(verbose_name='Пятница', blank=True, null=True, help_text=help_text)
    saturday = models.TimeField(verbose_name='Суббота', blank=True, null=True, help_text=help_text)
    sunday = models.TimeField(verbose_name='Воскресенье', blank=True, null=True, help_text=help_text)
    time_profile_data =  models.JSONField(verbose_name='Хранилище экземпляра', blank=True, default=dict, editable=False)

    def __str__(self) -> str:
        return self.name_time_profile
