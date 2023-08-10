import re
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from app_time_profile.models import TimeProfile

COLOR_CHOICES =(
    ("0be61600", "Зелёный"),
    ("0be61600", "Красный"),
    ("0be61600", "Синий"),
    ("0be61600", "Чёрный"),
    ("0be61600", "Жёлтый"),
)


class Checkpoint(models.Model):
    name_checkpoint = models.CharField(verbose_name='Имя проходной', max_length=50, unique=True)
    description_checkpoint = models.TextField(verbose_name='Описание проходной', max_length=250)
    data_checkpoint = models.JSONField(editable=False, verbose_name='Остальное о проходной', default=dict)

    class Meta:
        verbose_name = 'Проходная'
        verbose_name_plural = 'Проходные'

    def __str__(self) -> str:
        return self.name_checkpoint


class Department(models.Model):
    name_departament = models.CharField(unique=True, max_length=75, help_text='Поле ввода названия депертамента', verbose_name='Департамент',)
    abbreviation = models.CharField(max_length=15, help_text='Поле ввода абривиатуры департамента', verbose_name='Аббревиатура',)
    send_macroscope = models.BooleanField(verbose_name='Отправить данный в ПО Macroscope', help_text='Отправить данный в ПО Macroscope', default=True)
    color_group = models.CharField(max_length=10, verbose_name='Цвет группы', help_text='Выбирите цвет группы', choices=COLOR_CHOICES, default='')
    interception = models.BooleanField(help_text='Перехват группы', verbose_name='Перехват')
    data_departament = models.JSONField(editable=False, help_text='Остальная информация о департаменте', verbose_name='Хранилище экземпляра', default=dict)

    class Meta:
        verbose_name = 'Департамент'
        verbose_name_plural = 'Департаменты'

    def __str__(self) -> str:
        return self.name_departament


class Position(models.Model):
    name_position = models.CharField(unique=True, max_length=75, help_text='Поле ввода названия должности', verbose_name='Должность',)
    data_position = models.JSONField(editable=False, verbose_name='Остальное о должности', default=dict)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self) -> str:
        return self.name_position


class AccessProfile(models.Model):
    name_access_profile = models.CharField(max_length=50, help_text='Поле ввода имени профиля доступа', verbose_name='Имя профиля доступа',)
    description_access_profile = models.TextField(max_length=50, help_text='Поле ввода описания профиля доступа', verbose_name='Описание профиля доступа',)
    checkpoints = models.ManyToManyField(Checkpoint, verbose_name='Проходные')

    class Meta:
        verbose_name = 'Профиль доступа'
        verbose_name_plural = 'Профили доступа'
    
    def __str__(self) -> str:
        return self.name_access_profile


def valid(value):
    if len(value) == 10:
        try:
            pass_number = re.match("^([0-9]{10})$", value).group(0)
        except:
            raise ValidationError(
                _("%(value)s не верный формат! Ожидалось ХХХХХХХХХХ"),
                params={"value": value},
            )
    elif len(value) == 9:
        try:
            pass_number = re.match("^([0-9]{3})([\D])([0-9]{5})$", value)
            part_1_pass_number = pass_number.group(1)
            part_3_pass_number = pass_number.group(3)
        except:
            raise ValidationError(
                _("%(value)s не верный формат! Ожидалось ХХХ.ХХХХХ"),
                params={"value": value},
            )
    else:
        raise ValidationError(
                _("%(value)s не верный формат!"),
                params={"value": value},
            )


class Staffs(models.Model):
    # =========================================
    # блок описания валидатора для тел номеров 
    phone_number_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    # проверяет значение, введенное для CharField
    # Hомера телефонов хранятся в формате E.164.
    # =========================================
    employee_photo = models.ImageField(upload_to='images/%Y-%m-%d/', blank=True, verbose_name='Фото')
    last_name = models.CharField(max_length=50, help_text='Поле ввода фамилии сотрудника', verbose_name='Фамилия',)
    first_name = models.CharField(max_length=50, help_text='Поле ввода имени сотрудника', verbose_name='Имя',)
    patronymic = models.CharField(blank=True, max_length=50, help_text='Поле ввода отчества(при наличии) сотрудника', verbose_name='Отчество',)
    phone_number = models.CharField(validators=[phone_number_regex,], unique=True, max_length=16, help_text='Поле ввода тел. номера сотрудника', verbose_name='Телефонный номер')
    home_address = models.CharField(blank=True, max_length=50, help_text='Поле ввода домашнего адреса', verbose_name='Домашний адрес',)
    car_number = models.CharField(blank=True, max_length=10, help_text='Поле ввода номера машины сотрудника', verbose_name='Номер машины')
    car_model = models.CharField(blank=True, max_length=10, help_text='Поле ввода марки машины сотрудника', verbose_name='Марка машины')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name='Департамент')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, verbose_name='Должность')
    access_profile = models.ForeignKey(AccessProfile, on_delete=models.SET_NULL, null=True, verbose_name='Профиль доступа')
    time_profale = models.ForeignKey(TimeProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Профиль доступа по времени')
    pass_number = models.CharField(validators=[valid], max_length=10, verbose_name='Номер пропуска', help_text='Поле для ввода номера пропуска', unique=True)
    data_staffs = models.JSONField(editable=False, verbose_name='Остальное о сотруднике', default=dict)
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def to_json(self):
        return {
            'employee_photo': self.employee_photo,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'patronymic': self.patronymic,
            'phone_number': self.phone_number,
            'home_address': self.home_address,
            'car_number': self.car_number,
            'car_model': self.car_model,
            'department': self.department,
            'position': self.position,
            'access_profile': self.access_profile,
            'time_profale': self.time_profale,
            'pass_number': self.pass_number,
            'data_staffs': self.data_staffs,
        }


    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name} {self.patronymic}'


class MonitorEvents(models.Model):
    operation_type = models.CharField(max_length=15, verbose_name='тип операции')
    time_created = models.DateTimeField(verbose_name='дата/время')
    card = models.CharField(max_length=13, verbose_name='номер карты события')
    staff = models.CharField(max_length=175, verbose_name='сотрудник', null=True, blank=True)
    controller = models.ForeignKey('app_controller.Controller', on_delete=models.SET_NULL, null=True, blank=True)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Проходная')
    granted = models.CharField(max_length=25, verbose_name='вердикт от check_access', null=True, blank=True)
    event = models.CharField(max_length=3, verbose_name='тип события от сигнала events', null=True, blank=True)
    flag = models.CharField(max_length=3, verbose_name='флаг события от сигнала events', null=True, blank=True)
    data_monitor_events = models.JSONField(editable=False, verbose_name='хранилище экземпляра', default=dict)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self) -> str:
        if self.staff is None:
            return f'{self.staff}'
        return self.staff
