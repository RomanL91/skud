from django.contrib import admin

from app_time_profile.models import TimeProfile


@admin.register(TimeProfile)
class TimeProfileAdmin(admin.ModelAdmin):
    pass