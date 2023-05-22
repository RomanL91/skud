# Generated by Django 4.1.6 on 2023-05-22 04:49

import app_skud.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("app_controller", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name_access_profile",
                    models.CharField(
                        help_text="Поле ввода имени профиля доступа",
                        max_length=50,
                        verbose_name="Имя профиля доступа",
                    ),
                ),
                (
                    "description_access_profile",
                    models.TextField(
                        help_text="Поле ввода описания профиля доступа",
                        max_length=50,
                        verbose_name="Описание профиля доступа",
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль доступа",
                "verbose_name_plural": "Профили доступа",
            },
        ),
        migrations.CreateModel(
            name="Checkpoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name_checkpoint",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Имя проходной"
                    ),
                ),
                (
                    "description_checkpoint",
                    models.TextField(max_length=250, verbose_name="Описание проходной"),
                ),
                (
                    "data_checkpoint",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        verbose_name="Остальное о проходной",
                    ),
                ),
            ],
            options={
                "verbose_name": "Проходная",
                "verbose_name_plural": "Проходные",
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name_departament",
                    models.CharField(
                        help_text="Поле ввода названия депертамента",
                        max_length=75,
                        unique=True,
                        verbose_name="Департамент",
                    ),
                ),
                (
                    "abbreviation",
                    models.CharField(
                        help_text="Поле ввода абривиатуры департамента",
                        max_length=15,
                        verbose_name="Аббревиатура",
                    ),
                ),
                (
                    "send_macroscope",
                    models.BooleanField(
                        default=True,
                        help_text="Отправить данный в ПО Macroscope",
                        verbose_name="Отправить данный в ПО Macroscope",
                    ),
                ),
                (
                    "color_group",
                    models.CharField(
                        choices=[
                            ("0be61600", "Зелёный"),
                            ("0be61600", "Красный"),
                            ("0be61600", "Синий"),
                            ("0be61600", "Чёрный"),
                            ("0be61600", "Жёлтый"),
                        ],
                        default="",
                        help_text="Выбирите цвет группы",
                        max_length=10,
                        verbose_name="Цвет группы",
                    ),
                ),
                (
                    "interception",
                    models.BooleanField(
                        help_text="Перехват группы", verbose_name="Перехват"
                    ),
                ),
                (
                    "data_departament",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        help_text="Остальная информация о департаменте",
                        verbose_name="Хранилище экземпляра",
                    ),
                ),
            ],
            options={
                "verbose_name": "Департамент",
                "verbose_name_plural": "Департаменты",
            },
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name_position",
                    models.CharField(
                        help_text="Поле ввода названия должности",
                        max_length=75,
                        unique=True,
                        verbose_name="Должность",
                    ),
                ),
                (
                    "data_position",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        verbose_name="Остальное о должности",
                    ),
                ),
            ],
            options={
                "verbose_name": "Должность",
                "verbose_name_plural": "Должности",
            },
        ),
        migrations.CreateModel(
            name="Staffs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "employee_photo",
                    models.ImageField(
                        blank=True, upload_to="images/%Y-%m-%d/", verbose_name="Фото"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        help_text="Поле ввода фамилии сотрудника",
                        max_length=50,
                        verbose_name="Фамилия",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        help_text="Поле ввода имени сотрудника",
                        max_length=50,
                        verbose_name="Имя",
                    ),
                ),
                (
                    "patronymic",
                    models.CharField(
                        blank=True,
                        help_text="Поле ввода отчества(при наличии) сотрудника",
                        max_length=50,
                        verbose_name="Отчество",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        help_text="Поле ввода тел. номера сотрудника",
                        max_length=16,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                regex="^\\+?1?\\d{8,15}$"
                            )
                        ],
                        verbose_name="Телефонный номер",
                    ),
                ),
                (
                    "home_address",
                    models.CharField(
                        blank=True,
                        help_text="Поле ввода домашнего адреса",
                        max_length=50,
                        verbose_name="Домашний адрес",
                    ),
                ),
                (
                    "car_number",
                    models.CharField(
                        blank=True,
                        help_text="Поле ввода номера машины сотрудника",
                        max_length=10,
                        verbose_name="Номер машины",
                    ),
                ),
                (
                    "car_model",
                    models.CharField(
                        blank=True,
                        help_text="Поле ввода марки машины сотрудника",
                        max_length=10,
                        verbose_name="Марка машины",
                    ),
                ),
                (
                    "pass_number",
                    models.CharField(
                        help_text="Поле для ввода номера пропуска",
                        max_length=10,
                        unique=True,
                        validators=[app_skud.models.valid],
                        verbose_name="Номер пропуска",
                    ),
                ),
                (
                    "data_staffs",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        verbose_name="Остальное о сотруднике",
                    ),
                ),
                (
                    "access_profile",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app_skud.accessprofile",
                        verbose_name="Профиль доступа",
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app_skud.department",
                        verbose_name="Департамент",
                    ),
                ),
                (
                    "position",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app_skud.position",
                        verbose_name="Должность",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сотрудник",
                "verbose_name_plural": "Сотрудники",
            },
        ),
        migrations.CreateModel(
            name="MonitorEvents",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "operation_type",
                    models.CharField(max_length=15, verbose_name="тип операции"),
                ),
                ("time_created", models.DateTimeField(verbose_name="время создания")),
                (
                    "card",
                    models.CharField(max_length=13, verbose_name="номер карты события"),
                ),
                (
                    "staff",
                    models.CharField(
                        blank=True, max_length=175, null=True, verbose_name="сотрудник"
                    ),
                ),
                (
                    "granted",
                    models.CharField(
                        blank=True,
                        max_length=25,
                        null=True,
                        verbose_name="вердикт от check_access",
                    ),
                ),
                (
                    "event",
                    models.CharField(
                        blank=True,
                        max_length=3,
                        null=True,
                        verbose_name="тип события от сигнала events",
                    ),
                ),
                (
                    "flag",
                    models.CharField(
                        blank=True,
                        max_length=3,
                        null=True,
                        verbose_name="флаг события от сигнала events",
                    ),
                ),
                (
                    "data_monitor_events",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        verbose_name="хранилище экземпляра",
                    ),
                ),
                (
                    "checkpoint",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app_skud.checkpoint",
                    ),
                ),
                (
                    "controller",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app_controller.controller",
                    ),
                ),
            ],
            options={
                "verbose_name": "Событие",
                "verbose_name_plural": "События",
            },
        ),
        migrations.AddField(
            model_name="accessprofile",
            name="checkpoints",
            field=models.ManyToManyField(
                to="app_skud.checkpoint", verbose_name="Проходные"
            ),
        ),
    ]
