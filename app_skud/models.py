from django.db import models
from django.core.validators import RegexValidator


class Checkpoint(models.Model):
    name_checkpoint = models.CharField(verbose_name='Имя проходной', max_length=50, unique=True)
    description_checkpoint = models.TextField(verbose_name='Описание проходной', max_length=250)
    data_checkpoint = models.JSONField(editable=False, verbose_name='Остальное о проходной', default=dict)

    def __str__(self) -> str:
        return self.name_checkpoint


class Department(models.Model):
    name_departament = models.CharField(unique=True, max_length=75, help_text='Поле ввода названия депертамента', verbose_name='Департамент',)
    abbreviation = models.CharField(max_length=15, help_text='Поле ввода абривиатуры департамента', verbose_name='Аббревиатура',)
    data_departament = models.JSONField(editable=False, help_text='Остальная информация о департаменте', verbose_name='Хранилище экземпляра', default=dict)

    def __str__(self) -> str:
        return self.name_departament


class Position(models.Model):
    name_position = models.CharField(unique=True, max_length=75, help_text='Поле ввода названия должности', verbose_name='Должность',)
    data_position = models.JSONField(editable=False, verbose_name='Остальное о должности', default=dict)

    def __str__(self) -> str:
        return self.name_position


class AccessProfile(models.Model):
    name_access_profile = models.CharField(max_length=50, help_text='Поле ввода имени профиля доступа', verbose_name='Имя профиля доступа',)
    description_access_profile = models.TextField(max_length=50, help_text='Поле ввода описания профиля доступа', verbose_name='Описание профиля доступа',)
    checkpoints = models.ManyToManyField(Checkpoint)
    
    def __str__(self) -> str:
        return self.name_access_profile


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
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    access_profile = models.ForeignKey(AccessProfile, on_delete=models.SET_NULL, null=True)
    pass_number = models.PositiveIntegerField(verbose_name='Номер пропуска', help_text='Поле для ввода номера пропуска', unique=True)
    data_staffs = models.JSONField(editable=False, verbose_name='Остальное о сотруднике', default=dict)
    
    def __str__(self) -> str:
        return f'{self.last_name} {self.first_name} {self.patronymic}'


class MonitorCheckAccess(models.Model):
    staff = models.ForeignKey(Staffs, on_delete=models.SET_NULL, null=True, blank=True)
    controller = models.ForeignKey('app_controller.Controller', on_delete=models.SET_NULL, null=True, blank=True)
    data_monitor = models.JSONField(editable=False, verbose_name='хранилище экземпляра', default=dict)

    def __str__(self) -> str:
        return self.staff.last_name

    
