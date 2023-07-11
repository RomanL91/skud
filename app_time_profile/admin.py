from django.contrib import admin

from app_time_profile.models import TimeProfile


@admin.register(TimeProfile)
class TimeProfileAdmin(admin.ModelAdmin):
    fields = [
        ('name_time_profile',
        'descriptions',),
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]