from django.db import models

from app_skud.models import Staffs

from django.core.validators import RegexValidator



class TelegramPusher(models.Model):
    phone_number_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$")

    last_name = models.CharField(max_length=50, help_text='Поле ввода фамилии получателя уведомлений', verbose_name='Фамилия',)
    first_name = models.CharField(max_length=50, help_text='Поле ввода имени получателя уведомлений', verbose_name='Имя',)
    patronymic = models.CharField(blank=True, max_length=50, help_text='Поле ввода отчества(при наличии) получателя уведомлений', verbose_name='Отчество',)
    phone_number = models.CharField(validators=[phone_number_regex,], max_length=16, help_text='Поле ввода тел. номера куда будут приходить уведомления (TELEGRAM)', verbose_name='Телефонный номер')
    
    object_pusher = models.ManyToManyField(Staffs, verbose_name='Объект уведомления', help_text='Выберите людей о чьих действиях Вы будете уведомлены')

    secret_pass = models.CharField(max_length=50, help_text='Поле ввода секретного ключа, для регистрации в Боте (запомните его)', verbose_name='Секрктный ключ',)

    status = models.BooleanField(verbose_name='Статус авторизации', help_text='При прохождении решистрации в Боте - статус будет активным')

    def __str__(self) -> str:
        return self.phone_number
    