# Generated by Django 4.1.6 on 2023-02-10 07:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_controller', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_access_profile', models.CharField(help_text='Поле ввода имени профиля доступа', max_length=50, verbose_name='Имя профиля доступа')),
                ('description_access_profile', models.TextField(help_text='Поле ввода описания профиля доступа', max_length=50, verbose_name='Описание профиля доступа')),
            ],
        ),
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_checkpoint', models.CharField(max_length=50, unique=True, verbose_name='Имя проходной')),
                ('description_checkpoint', models.TextField(max_length=250, verbose_name='Описание проходной')),
                ('data_checkpoint', models.JSONField(default=dict, editable=False, verbose_name='Остальное о проходной')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_departament', models.CharField(help_text='Поле ввода названия депертамента', max_length=75, unique=True, verbose_name='Департамент')),
                ('abbreviation', models.CharField(help_text='Поле ввода абривиатуры департамента', max_length=15, verbose_name='Аббревиатура')),
                ('data_departament', models.JSONField(default=dict, editable=False, help_text='Остальная информация о департаменте', verbose_name='Хранилище экземпляра')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_position', models.CharField(help_text='Поле ввода названия должности', max_length=75, unique=True, verbose_name='Должность')),
                ('data_position', models.JSONField(default=dict, editable=False, verbose_name='Остальное о должности')),
            ],
        ),
        migrations.CreateModel(
            name='Staffs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(help_text='Поле ввода фамилии сотрудника', max_length=50, verbose_name='Фамилия')),
                ('first_name', models.CharField(help_text='Поле ввода имени сотрудника', max_length=50, verbose_name='Имя')),
                ('patronymic', models.CharField(blank=True, help_text='Поле ввода отчества(при наличии) сотрудника', max_length=50, verbose_name='Отчество')),
                ('phone_number', models.CharField(help_text='Поле ввода тел. номера сотрудника', max_length=16, unique=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{8,15}$')], verbose_name='Телефонный номер')),
                ('home_address', models.CharField(blank=True, help_text='Поле ввода домашнего адреса', max_length=50, verbose_name='Домашний адрес')),
                ('car_number', models.CharField(blank=True, help_text='Поле ввода номера машины сотрудника', max_length=10, unique=True, verbose_name='Номер машины')),
                ('car_model', models.CharField(blank=True, help_text='Поле ввода марки машины сотрудника', max_length=10, verbose_name='Марка машины')),
                ('pass_number', models.PositiveIntegerField(help_text='Поле для ввода номера пропуска', unique=True, verbose_name='Номер пропуска')),
                ('data_staffs', models.JSONField(default=dict, editable=False, verbose_name='Остальное о сотруднике')),
                ('access_profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_skud.accessprofile')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_skud.department')),
                ('position', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_skud.position')),
            ],
        ),
        migrations.CreateModel(
            name='MonitorCheckAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controller', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_controller.controller')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_skud.staffs')),
            ],
        ),
        migrations.AddField(
            model_name='accessprofile',
            name='checkpoints',
            field=models.ManyToManyField(to='app_skud.checkpoint'),
        ),
    ]
