# Generated by Django 4.1.6 on 2023-05-22 04:49

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Controller",
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
                    "controller_type",
                    models.CharField(max_length=20, verbose_name="Тип контроллера"),
                ),
                (
                    "serial_number",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="Серийный номер контроллера"
                    ),
                ),
                (
                    "controller_activity",
                    models.CharField(
                        choices=[("1", "active"), ("0", "desactive")],
                        max_length=2,
                        verbose_name="активность контроллера",
                    ),
                ),
                (
                    "controller_online",
                    models.CharField(
                        choices=[("1", "online"), ("0", "offline")],
                        default="0",
                        max_length=2,
                        verbose_name="режим онлайн контроллера",
                    ),
                ),
                (
                    "controller_mode",
                    models.CharField(
                        choices=[
                            ("0", "norma"),
                            ("1", "block"),
                            ("2", "free"),
                            ("3", "waiting for free passage"),
                        ],
                        max_length=2,
                        verbose_name="режим работы контроллера",
                    ),
                ),
                (
                    "data_settings_zone",
                    models.JSONField(
                        default=dict,
                        editable=False,
                        verbose_name="настройки зон контроллера",
                    ),
                ),
                (
                    "other_data",
                    models.JSONField(
                        default=dict, editable=False, verbose_name="остальные настройки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Контроллер",
                "verbose_name_plural": "Контроллеры",
            },
        ),
    ]
