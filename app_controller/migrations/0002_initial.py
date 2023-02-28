# Generated by Django 4.1.6 on 2023-02-10 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_controller', '0001_initial'),
        ('app_skud', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_initiator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_skud.staffs'),
        ),
        migrations.AddField(
            model_name='controller',
            name='checkpoint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_skud.checkpoint'),
        ),
    ]
