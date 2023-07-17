from datetime import time

from django.contrib import admin

from app_time_profile.models import TimeProfile


@admin.register(TimeProfile)
class TimeProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name_time_profile', 'descriptions')}),
        ('Понедельник', {'fields': (('monday_time_stert', 'monday_time_end'),), 'classes':('collapse',)}),
        ('Вторник', {'fields': (('tuesday_time_start', 'tuesday_time_end'),), 'classes':('collapse',)}),
        ('Среда', {'fields': (('wednesday_time_start', 'wednesday_time_end'),), 'classes':('collapse',)}),
        ('Четверг', {'fields': (('thursday_time_start', 'thursday_time_end'),), 'classes':('collapse',)}),
        ('Пятница', {'fields': (('friday_time_start', 'friday_time_end'),), 'classes':('collapse',)}),
        ('Суббота', {'fields': (('saturday_time_start', 'saturday_time_end'),), 'classes':('collapse',)}),
        ('Воскресенье', {'fields': (('sunday_time_start', 'sunday_time_end'),), 'classes':('collapse',)}),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        for field, value in obj.__dict__.copy().items():
            if value == None:
                if field[-3:] == 'end':
                    obj.__dict__[field] = time(23, 59, 59)
                else:
                    obj.__dict__[field] = time(00, 00, 1)

        week_data = {
            'monday': (obj.monday_time_stert.strftime('%H:%M:%S'), obj.monday_time_end.strftime('%H:%M:%S')),
            'tuesday': (obj.tuesday_time_start.strftime('%H:%M:%S'), obj.tuesday_time_end.strftime('%H:%M:%S')),
            'wednesday': (obj.wednesday_time_start.strftime('%H:%M:%S'), obj.wednesday_time_end.strftime('%H:%M:%S')),
            'thursday': (obj.thursday_time_start.strftime('%H:%M:%S'), obj.thursday_time_end.strftime('%H:%M:%S')),
            'friday': (obj.friday_time_start.strftime('%H:%M:%S'), obj.friday_time_end.strftime('%H:%M:%S')),
            'saturday': (obj.saturday_time_start.strftime('%H:%M:%S'), obj.saturday_time_end.strftime('%H:%M:%S')),
            'sunday': (obj.sunday_time_start.strftime('%H:%M:%S'), obj.sunday_time_end.strftime('%H:%M:%S')),
        }
        obj.time_profile_data = week_data
        obj.save()