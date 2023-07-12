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