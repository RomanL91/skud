# Generated by Django 4.1.6 on 2023-02-10 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_controller', '0002_initial'),
        ('app_skud', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitorcheckaccess',
            name='controller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_controller.controller'),
        ),
        migrations.AlterField(
            model_name='monitorcheckaccess',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_skud.staffs'),
        ),
    ]
