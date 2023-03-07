import json, asyncio
from django.contrib import admin
from django.utils.html import mark_safe

from .models import (
    Checkpoint, Staffs, Department, 
    Position, AccessProfile, MonitorCheckAccess,
    MonitorEvents
)

from app_controller.functions_working_database import (
    get_all_available_passes_for_employee,
    get_list_all_controllers_available_for_object,
)

from app_controller.server_signals import (
    URL,
    ADD_CARD,
    send_GET_request_for_controllers, 
    async_send_GET_request_for_controllers
)

from app_controller.views import (
    ResponseModel
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
    
    def get_image(self, obj):
        if obj.employee_photo:
            return mark_safe(f'<img src={obj.employee_photo.url} width="50" height="50"')
        else:
            return None

    get_image.short_description = 'ФОТО'

    def response_post_save_add(self, request, obj):
        list_checkpoints_for_obj = get_all_available_passes_for_employee(obj=obj)
        list_controllers_for_obj = get_list_all_controllers_available_for_object(query_set_checkpoint=list_checkpoints_for_obj)
        mask = ['000000']
        pass_number = request.POST['pass_number']
        pass_number_len = len(pass_number)
        if pass_number_len > 10 or pass_number_len < 9:
            raise ValueError('Длина номера карты не может быть больше 10 или меньше 9 символов.')
        else:
            try:
                serial, number = pass_number.split('.')
                if len(serial) != 3 or len(number) != 5:
                    raise ValueError('ERROR')
                hex_serial = hex(int(serial))[2:]
                mask.append(hex_serial)
                hex_number = hex(int(number))[2:]
                mask.append(hex_number)
                hex_pass_number = ''.join(mask).upper()
                obj.pass_number = hex_pass_number
                obj.save()
            except:
                if pass_number_len == 10:
                    hex_pass_number = hex(int(pass_number))[2:]
                    mask.append(hex_pass_number)
                    hex_pass_number = ''.join(mask).upper()
                    obj.pass_number = hex_pass_number
                    obj.save()
                else:
                    raise ValueError('pass')
                
        for controller in list_controllers_for_obj:
            serial_number = controller.serial_number
            signal_add_card = ADD_CARD(card_number=hex_pass_number)
            response = ResponseModel(message_reply=signal_add_card, serial_number_controller=serial_number)
            response_serializer = json.dumps(response)
            send_GET_request_for_controllers(url=URL, data=response_serializer)

        return self._response_post_save(request, obj)

        
@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = ACCESS_PROFILE_LIST
    list_filter = ACCESS_PROFILE_LIST + ['checkpoints',]


@admin.register(MonitorCheckAccess)
class MonitorCheckAccessAdmin(admin.ModelAdmin):
    list_display = MONITOR_CHECK_ACCESS_LIST
    list_filter = MONITOR_CHECK_ACCESS_LIST


@admin.register(MonitorEvents)
class MonitorEventsAdmin(admin.ModelAdmin):
    pass
