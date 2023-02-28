from django.contrib import admin
from django.utils.html import mark_safe

from .models import (
    Checkpoint, Staffs, Department, 
    Position, AccessProfile, MonitorCheckAccess
)


admin.site.register(Checkpoint)
admin.site.register(Department)
admin.site.register(Position)


STAFF_LIST_DISPLAY = [
    # 'employee_photo',
    'last_name', 'first_name', 'patronymic',
    'phone_number', 'home_address', 'car_number',
    'car_model', 'department', 'position',
    'access_profile', 'pass_number', 'data_staffs',
]

ACCESS_PROFILE_LIST = [
    'name_access_profile',
    'description_access_profile',
    # 'checkpoints',
]

MONITOR_CHECK_ACCESS_LIST = [
    'staff',
    'controller',
    'data_monitor',
]

@admin.register(Staffs)
class StaffAdmin(admin.ModelAdmin):
    list_display = STAFF_LIST_DISPLAY + ['get_image',]
    list_filter = STAFF_LIST_DISPLAY
    readonly_fields = ['get_image',]
    # search_fields = []
    
    def get_image(self, obj):
        if obj.employee_photo:
            return mark_safe(f'<img src={obj.employee_photo.url} width="50" height="50"')
        else:
            return None

    get_image.short_description = 'ФОТО'

    
    
@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = ACCESS_PROFILE_LIST
    list_filter = ACCESS_PROFILE_LIST + ['checkpoints',]


@admin.register(MonitorCheckAccess)
class MonitorCheckAccessAdmin(admin.ModelAdmin):
    list_display = MONITOR_CHECK_ACCESS_LIST
    list_filter = MONITOR_CHECK_ACCESS_LIST




