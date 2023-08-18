from django.contrib import admin

from app_observer.models import PerimeterMonitor


@admin.register(PerimeterMonitor)
class PerimeterMonitorAdmin(admin.ModelAdmin):
    pass
