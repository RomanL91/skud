import json

from django.shortcuts import render, redirect
from django.urls import re_path

from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models

from .models import (
    Checkpoint, Staffs, Department, 
    Position, AccessProfile, 
    MonitorEvents
)

from app_controller.models import (
    Controller
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
    'last_name', 'first_name', 'patronymic',
    'phone_number', 
    'department', 'position',
    'access_profile', 'pass_number', 
]

ACCESS_PROFILE_LIST = [
    'name_access_profile',
    'description_access_profile',
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
]

STAFF_LIST_EDITABLE = [
    'phone_number', 'home_address', 'car_number',
    'car_model', 'department', 'position',
    'access_profile', 
]


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                '<a href="{}" target="_blank"><img src="{}" alt="{}" style="max-height: 200px;"/></a>'.
                    format(image_url, image_url, file_name))
        output.append(super().render(name, value, attrs))
        return mark_safe(u''.join(output))

from django.contrib.admin.utils import construct_change_message
@admin.register(Staffs)
class StaffAdmin(admin.ModelAdmin):
    list_display = STAFF_LIST_DISPLAY + ['get_image',] 
    list_filter = STAFF_LIST_DISPLAY
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    
    def get_image(self, obj):
        if obj.employee_photo:
            return mark_safe(f'<img src={obj.employee_photo.url} width="50" height="50"')
        else:
            return None

    get_image.short_description = 'ФОТО'


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            obj_from_BD = Staffs.objects.get(pk=object_id)
            pass_number_obj_from_BD = obj_from_BD.pass_number
            list_checkpoints_obj_from_BD = obj_from_BD.access_profile.checkpoints.all()
            access_profile_obj_from_BD_pk = obj_from_BD.access_profile.pk
        except:
            list_checkpoints_obj_from_BD = None
            access_profile_obj_from_BD_pk = None
            obj_from_BD =None
            pass_number_obj_from_BD = None
        # код ниже требует рефакторинга(DRY)
        if request.method == 'POST':
            form = request.POST
            request_access_profile = int(form.get('access_profile'))
            request_pass_number = form.get('pass_number')
            # если истина, то важные изменения (профиль доступа или номер пропуска)
            if access_profile_obj_from_BD_pk != request_access_profile or pass_number_obj_from_BD != request_pass_number:
                # истина, если изменен номер пропуска, а профиль доступа без изменения
                if pass_number_obj_from_BD != request_pass_number and access_profile_obj_from_BD_pk == request_access_profile:
                    print('изменен ключ сотрудника')
                    list_controllers = []
                    for checkpoint in list_checkpoints_obj_from_BD:
                        controller = Controller.objects.get(checkpoint=checkpoint)
                        list_controllers.append(controller)
                    print(f'list_controllers --->>> {list_controllers}')
                    signal_del_card = DEL_CARDS(card_number=pass_number_obj_from_BD)
                    print(f'signal_del_card --->>> {signal_del_card}')
                    signal_add_card = ADD_CARD(card_number=request_pass_number)
                    print(f'signal_add_card --->>> {signal_add_card}')

                    for el in list_controllers:
                        send_GET_request_for_controllers(
                            url=el.other_data['controller_ip'],
                            data=json.dumps(
                                ResponseModel(
                                    message_reply=signal_del_card,
                                    serial_number_controller=el.serial_number
                                )
                            )
                        )
                        send_GET_request_for_controllers(
                            url=el.other_data['controller_ip'],
                            data=json.dumps(
                                ResponseModel(
                                    message_reply=signal_add_card,
                                    serial_number_controller=el.serial_number
                                )
                            )
                        )

                # истина, если номер пропуска без изменения, а профиль доступа изменен
                if pass_number_obj_from_BD == request_pass_number and access_profile_obj_from_BD_pk != request_access_profile:
                    print('изменен профиль доступа')
                    new_access_profile = AccessProfile.objects.get(pk=request_access_profile)
                    list_checkpoints_new_access_profile = new_access_profile.checkpoints.all()
                    print(f'list_checkpoints_obj_from_BD --->>> {list_checkpoints_obj_from_BD}')
                    print(f'list_checkpoints_new_access_profile --->>> {list_checkpoints_new_access_profile}')

                    if len(list_checkpoints_obj_from_BD) > len(list_checkpoints_new_access_profile):
                        print('сужение профиля доступа')
                        list_checkpoints_remove_card = [el for el in list_checkpoints_obj_from_BD if el not in list_checkpoints_new_access_profile]
                        print(f'проходные с которых нужно удалить карту --->>> {list_checkpoints_remove_card}')
                        signal_del_card = DEL_CARDS(card_number=pass_number_obj_from_BD)
                        list_controllers = []
                        for checkpoint in list_checkpoints_remove_card:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers.append(controller)
                        for el in list_controllers:
                            send_GET_request_for_controllers(
                                url=el.other_data['controller_ip'],
                                data=json.dumps(
                                    ResponseModel(
                                        message_reply=signal_del_card,
                                        serial_number_controller=el.serial_number
                                    )
                                )
                            )
                        
                    elif len(list_checkpoints_obj_from_BD) < len(list_checkpoints_new_access_profile):
                        print('расширение профиля доступа')
                        list_checkpoints_add_card = [el for el in list_checkpoints_new_access_profile if el not in list_checkpoints_obj_from_BD]
                        print(f'контроллеры в которые нужно добавить карту --->>> {list_checkpoints_add_card}')
                        signal_add_card = ADD_CARD(card_number=pass_number_obj_from_BD)
                        list_controllers = []
                        for checkpoint in list_checkpoints_add_card:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers.append(controller)
                        for el in list_controllers:
                            send_GET_request_for_controllers(
                                url=el.other_data['controller_ip'],
                                data=json.dumps(
                                    ResponseModel(
                                        message_reply=signal_add_card,
                                        serial_number_controller=el.serial_number
                                    )
                                )
                            )
                    else:
                        signal_del_card = DEL_CARDS(card_number=pass_number_obj_from_BD)
                        signal_add_card = ADD_CARD(card_number=pass_number_obj_from_BD)
                        print('нужно поэлементное сравнение')
                        list_checkpoints_remove_card = [el for el in list_checkpoints_obj_from_BD if el not in list_checkpoints_new_access_profile]
                        print(f'list_checkpoints_remove_card ------>>> {list_checkpoints_remove_card}')
                        list_controllers_for_del_card = []
                        for checkpoint in list_checkpoints_remove_card:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers_for_del_card.append(controller)
                        for el in list_controllers_for_del_card:
                            send_GET_request_for_controllers(
                                url=el.other_data['controller_ip'],
                                data=json.dumps(
                                    ResponseModel(
                                        message_reply=signal_del_card,
                                        serial_number_controller=el.serial_number
                                    )
                                )
                            )

                        list_controllers_add_card = [el for el in list_checkpoints_new_access_profile if el not in list_checkpoints_obj_from_BD]
                        print(f'list_controllers_add_card ------>>> {list_controllers_add_card}')
                        list_controllers_for_add_card = []
                        for checkpoint in list_controllers_add_card:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers_for_add_card.append(controller)
                        for el in list_controllers_for_add_card:
                            send_GET_request_for_controllers(
                                url=el.other_data['controller_ip'],
                                data=json.dumps(
                                    ResponseModel(
                                        message_reply=signal_add_card,
                                        serial_number_controller=el.serial_number
                                    )
                                )
                            )
                
                # истина, если номер пропуска изменен и профиль доступа
                if pass_number_obj_from_BD != request_pass_number and access_profile_obj_from_BD_pk != request_access_profile:
                    print('изменен ключ и профиль доступа сотрудника')
                    list_controllers_for_del_card = []
                    try:
                        for checkpoint in list_checkpoints_obj_from_BD:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers_for_del_card.append(controller)
                        signal_del_card = DEL_CARDS(card_number=pass_number_obj_from_BD)
                    except:
                        pass
                    for el in list_controllers_for_del_card:
                        send_GET_request_for_controllers(
                            url=el.other_data['controller_ip'],
                            data=json.dumps(
                                ResponseModel(
                                    message_reply=signal_del_card,
                                    serial_number_controller=el.serial_number
                                )
                            )
                        )
                    new_access_profile = AccessProfile.objects.get(pk=request_access_profile)
                    list_checkpoints_new_access_profile = new_access_profile.checkpoints.all()
                    print(f'проходные нового профиля -----> {list_checkpoints_new_access_profile}')
                    list_controllers_add_card = []
                    try:
                        for checkpoint in list_checkpoints_new_access_profile:
                            controller = Controller.objects.get(checkpoint=checkpoint)
                            list_controllers_add_card.append(controller)

                        mask = ['000000']
                        hex_pass_number = hex(int(request_pass_number))[2:]
                        mask.append(hex_pass_number)
                        hex_pass_number = ''.join(mask).upper()


                        signal_add_card = ADD_CARD(card_number=hex_pass_number)
                        print(f'list_controllers_add_card -----> {list_controllers_add_card}')
                    except Exception as e:
                        pass

                    mask = ['000000']
                    hex_pass_number = hex(int(request_pass_number))[2:]
                    mask.append(hex_pass_number)
                    hex_pass_number = ''.join(mask).upper()


                    for el in list_controllers_add_card:
                        print(f'---отсылаю сигнал добавления карты---')
                        send_GET_request_for_controllers(
                            url=el.other_data['controller_ip'],
                            data=json.dumps(
                                ResponseModel(
                                    message_reply=signal_add_card,
                                    serial_number_controller=el.serial_number
                                )
                            )
                        )
            else:
                print('никаких важных изменений')

        extra_context = extra_context or {}
        extra_context['show_save'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)


#     def response_post_save_add(self, request, obj):
#         list_checkpoints_for_obj = get_all_available_passes_for_employee(obj=obj)
#         list_controllers_for_obj = get_list_all_controllers_available_for_object(query_set_checkpoint=list_checkpoints_for_obj)
#         mask = ['000000']
#         pass_number = request.POST['pass_number']
#         pass_number_len = len(pass_number)
#         if pass_number_len > 10 or pass_number_len < 9:
#             self.message_user(request=request, message=f'Длина номера карты не может быть больше 10 или меньше 9 символов.', level='error')
#             obj.delete()
#             return self._response_post_save(request, obj)

#         else:
#             try:
#                 serial, number = pass_number.split('.')
#                 if len(serial) != 3 or len(number) != 5:
#                     raise ValueError('ERROR')
#                 hex_serial = hex(int(serial))[2:]
#                 mask.append(hex_serial)
#                 hex_number = hex(int(number))[2:]
#                 mask.append(hex_number)
#                 hex_pass_number = ''.join(mask).upper()
#                 obj.pass_number = hex_pass_number
#                 obj.save()
#             except:
#                 if pass_number_len == 10:
#                     hex_pass_number = hex(int(pass_number))[2:]
#                     mask.append(hex_pass_number)
#                     hex_pass_number = ''.join(mask).upper()
#                     obj.pass_number = hex_pass_number
#                     obj.save()
#                 else:
#                     raise ValueError('pass')
# # ДУБЛИРОВАНИЕ ================================
#         for controller in list_controllers_for_obj:
#             controller_url = controller.other_data["controller_ip"]
#             serial_number = controller.serial_number
#             signal_add_card = ADD_CARD(card_number=hex_pass_number)
#             response = ResponseModel(message_reply=signal_add_card, serial_number_controller=serial_number)
#             response_serializer = json.dumps(response)
#             send_GET_request_for_controllers(url=controller_url, data=response_serializer)

#         return self._response_post_save(request, obj)
    
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
    list_display = ACCESS_PROFILE_LIST
    list_filter = ACCESS_PROFILE_LIST + ['checkpoints',]

    def delete_model(self, request, obj):
        checkpoints_list_this_access_profile = obj.checkpoints.all()
        staffs_list_this_access_profile = Staffs.objects.filter(access_profile=obj.pk)
        list_pass_number_access_profile = [el.pass_number for el in staffs_list_this_access_profile]
        controller_list_this_access_profile = []
        for checpoint in checkpoints_list_this_access_profile:
            controller = Controller.objects.get(checkpoint=checpoint)
            controller_list_this_access_profile.append(controller)
        signal_del_cards = DEL_CARDS(card_number=list_pass_number_access_profile)
        for el in controller_list_this_access_profile:
            send_GET_request_for_controllers(url=el.other_data['controller_ip'],
                                             data=json.dumps(ResponseModel(message_reply=signal_del_cards,
                                                                           serial_number_controller=el.serial_number))
            )
        obj.delete()


from .forms import MonitorEventsModelForm
@admin.register(MonitorEvents)
class MonitorEventsAdmin(admin.ModelAdmin):
    list_display = MONITOR_EVENTS_LIST_DISPLAY
    list_filter = MONITOR_EVENTS_LIST_DISPLAY
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
