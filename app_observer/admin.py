from django.contrib import admin

from app_observer.models import PerimeterMonitor


@admin.register(PerimeterMonitor)
class PerimeterMonitorAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        # 'perimeter_gates',
        'perimeter_counter',
        'get_perimeter_gates',
        # 'perimeter_data',
    ]

    def get_perimeter_gates(self, obj):
        return " | ".join([checkpoint.name_checkpoint for checkpoint in obj.perimeter_gates.all()])
    get_perimeter_gates.short_description = 'Проходные'
