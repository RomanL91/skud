import json

from django.shortcuts import render, redirect
from django.urls import re_path

from django.contrib import admin
from django.utils.html import mark_safe

from .models import (
    Checkpoint, Staffs, Department, 
    Position, AccessProfile, 
    MonitorEvents
)

from app_controller.functions_working_database import (
    get_all_available_passes_for_employee,
    get_list_all_controllers_available_for_object,
    get_events_for_range_dates
)

from app_controller.server_signals import (
    ADD_CARD,
    DEL_CARDS,
    send_GET_request_for_controllers, 
    async_send_GET_request_for_controllers
)

from .f_export_from_DB import import_data_from_database

from app_controller.views import ResponseModel


# ==========================================================================================

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

MONITOR_EVENTS_LIST_DISPLAY = [
    'operation_type',
    'time_created',
    'card',
    'staff',
    'controller',
    'checkpoint',
    'granted',
    'event',
    'flag',
    'data_monitor_events',
]

STAFF_LIST_EDITABLE = [
    'phone_number', 'home_address', 'car_number',
    'car_model', 'department', 'position',
    'access_profile', 
]


@admin.register(Staffs)
class StaffAdmin(admin.ModelAdmin):
    list_display = STAFF_LIST_DISPLAY + ['get_image',]
    list_filter = STAFF_LIST_DISPLAY
    # list_editable = STAFF_LIST_EDITABLE
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
# ДУБЛИРОВАНИЕ ================================
        for controller in list_controllers_for_obj:
            controller_url = controller.other_data["controller_ip"]
            serial_number = controller.serial_number
            signal_add_card = ADD_CARD(card_number=hex_pass_number)
            response = ResponseModel(message_reply=signal_add_card, serial_number_controller=serial_number)
            response_serializer = json.dumps(response)
            send_GET_request_for_controllers(url=controller_url, data=response_serializer)

        return self._response_post_save(request, obj)
    
    def delete_model(self, request, obj):
        list_checkpoints_for_obj = get_all_available_passes_for_employee(obj=obj)
        list_controllers_for_obj = get_list_all_controllers_available_for_object(query_set_checkpoint=list_checkpoints_for_obj)
        card_number = obj.pass_number

        for controller in list_controllers_for_obj:
            controller_url = controller.other_data["controller_ip"]
            serial_number = controller.serial_number
            signal_del_card = DEL_CARDS(card_number=card_number)
            response = ResponseModel(message_reply=signal_del_card, serial_number_controller=serial_number)
            response_serializer = json.dumps(response)
            send_GET_request_for_controllers(url=controller_url, data=response_serializer)
# ДУБЛИРОВАНИЕ ================================

        obj.delete()
    
        
@admin.register(AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
    list_display = ACCESS_PROFILE_LIST
    list_filter = ACCESS_PROFILE_LIST + ['checkpoints',]

from .forms import MonitorEventsModelForm
@admin.register(MonitorEvents)
class MonitorEventsAdmin(admin.ModelAdmin):
    list_display = MONITOR_EVENTS_LIST_DISPLAY
    actions = ['delete_selected',]

    change_list_template = 'app_skud/admin/monitorevents_change_list.html'

    def get_urls(self):
        urls = super(MonitorEventsAdmin, self).get_urls()
        custom_urls = [
            re_path('^import/$', self.date_range_view_function, name='process_import'),]
        return custom_urls + urls
    
    def date_range_view_function(self, request):
        form = MonitorEventsModelForm(request.POST)

        if request.method == 'POST':
            if form.is_valid():
                staff = form.data['staff']
                checkpoint = form.data['checkpoint']
                departament = form.data['departament']
                start_date_for_filter = (
                    int(form.data['start_date_year']),
                    int(form.data['start_date_month']),
                    int(form.data['start_date_day']),
                )
                end_date_for_filter = (
                    int(form.data['end_date_year']),
                    int(form.data['end_date_month']),
                    int(form.data['end_date_day']),
                )

                if start_date_for_filter > end_date_for_filter:
                    self.message_user(request=request, message='Начальная дата не может быть больше конечной', level='error')
                    return redirect(to=request.META['HTTP_REFERER'])


                obj_BD_date_filter = get_events_for_range_dates(
                    start_date=start_date_for_filter,
                    end_date=end_date_for_filter
                )

                if staff != '':
                    staff_from_BD = Staffs.objects.get(pk=staff).__str__()
                    obj_BD_date_filter = obj_BD_date_filter.filter(staff=staff_from_BD)

                if checkpoint != '':
                    obj_BD_date_filter = obj_BD_date_filter.filter(checkpoint=checkpoint)

                if departament != '':
                    list_data_staffs = [staff.staff for staff in obj_BD_date_filter]
                    list_of_employees_filtered_by_department = []
                    for value in list_data_staffs:
                        try:
                            st = Staffs.objects.get(
                                last_name=value.split(' ')[0], 
                                first_name=value.split(' ')[1], 
                                patronymic=value.split(' ')[2], 
                                department=departament).__str__()
                            list_of_employees_filtered_by_department.append(st)
                        except:
                            continue


                    obj_BD_date_filter = [
                        i
                        for i in obj_BD_date_filter if i.staff in list_of_employees_filtered_by_department
                    ]

                if len(obj_BD_date_filter) == 0:
                    self.message_user(request=request, message='Не обнаружено событий, согласно указанным фильтрам', level='warning')
                    return redirect(to=request.META['HTTP_REFERER'])

                return import_data_from_database(request=request, data=obj_BD_date_filter)
        return render(request, 'app_skud/admin/unloading_events.html', context={'form': form})


@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]


@admin.register(Department)
class DepartamenAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
