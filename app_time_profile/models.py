import datetime

from django.db import models


help_text = 'Пожалуйста, используте установленный формат: ЧЧ:ММ'
ver_name_start_d = 'начало рабочего дня'
ver_name_end_d = 'конец рабочего дня'


def get_time_choices(start_time=datetime.time(0,0,0), end_time=datetime.time(23,0,0), delta=datetime.timedelta(minutes=15)):
    time_choices = ()
    time = start_time
    while time <= end_time:
        time_choices += ((time, time.strftime("%H:%M")),)
        time = (datetime.datetime.combine(datetime.date.today(), time) + delta).time()
    return time_choices

class TimeProfile(models.Model):
    name_time_profile = models.CharField(verbose_name='Название профиля доступа', unique=True, max_length= 150, help_text='Поле для ввода названия профиля доступа по времени')
    descriptions = models.TextField(verbose_name='Описание профиля доступа', blank=True, help_text='Поле для ввода описания данного профиля доступа по времени')
    
    monday_time_stert =  models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    monday_time_end =  models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    tuesday_time_start =  models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    tuesday_time_end =  models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    wednesday_time_start = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    wednesday_time_end = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    thursday_time_start = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    thursday_time_end = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    friday_time_start = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    friday_time_end = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    saturday_time_start = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    saturday_time_end = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)
    
    sunday_time_start = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_start_d, blank=True, null=True, help_text=help_text)
    sunday_time_end = models.TimeField(choices=get_time_choices(), verbose_name=ver_name_end_d, blank=True, null=True, help_text=help_text)

    time_profile_data =  models.JSONField(verbose_name='Хранилище экземпляра', blank=True, default=dict, editable=False)

    def __str__(self) -> str:
        return self.name_time_profile
