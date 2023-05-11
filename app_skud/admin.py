import json

from django.shortcuts import render, redirect
from django.urls import re_path
from django.contrib import messages


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

from app_skud.utils_to_microscope import (
    URL_API, POST_ADD_GRP_PREF, POST_UPDATE_GRP_PREF,
    login, passw, DELETE_FACE_PREF, GET_ID_FACE_MICROSCOPE,
    commands_RESTAPI_microscope, microscope_work_with_faces
    )

from app_controller.views import ResponseModel

from app_skud.utilities import (
    validation_and_formatting_of_pass_number, give_signal_to_controllers,
    validation_and_formatting_of_pass_number_form,
    work_with_controllers_when_an_employee_data_changes)


STAFF_LIST_DISPLAY = [
    'last_name', 'first_name', 'patronymic',
    'phone_number', 
    'department', 'position',
    'access_profile', 'pass_number', 'data_staffs'
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


from app_skud.forms import StaffsModelForm

@admin.register(Staffs)
class StaffAdmin(admin.ModelAdmin):
    list_display = STAFF_LIST_DISPLAY + ['get_image', 'face_detect'] 
    list_filter = STAFF_LIST_DISPLAY
    form = StaffsModelForm
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    
 
    def face_detect(self, obj):
        try:
            microscope = obj.data_staffs['microscope']
        except:
            microscope = False
        if microscope:
            return mark_safe(f'<img src="/media/galka.png" width="50" height="50"')
        else:
            return mark_safe(f'<img src="/media/krest.png" width="50" height="50"')
    face_detect.short_description = 'РАСПОЗОВАНИЕ ЛИЦ'


    def get_image(self, obj):
        if obj.employee_photo:
            return mark_safe(f'<img src={obj.employee_photo.url} width="50" height="50"')
        else:
            return None
    get_image.short_description = 'ФОТО'

 
    def save_model(self, request, obj, form, change):
        if change:
            old_pass_number = form.initial['pass_number']
            new_pass_number = form.cleaned_data['pass_number']
            old_access_profile_pk = form.initial['access_profile']
            new_access_profile_pk = form.cleaned_data['access_profile'].pk
            if old_pass_number != new_pass_number and old_access_profile_pk != new_access_profile_pk:
                print('изменен ключ и профиль сотрудника------------')
                hex_old_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=old_pass_number)
                hex_new_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=new_pass_number)
                all_checkpoints_old_access_profile = obj.access_profile.checkpoints.all()
                all_checkpoints_new_access_profile = AccessProfile.objects.get(pk=new_access_profile_pk).checkpoints.all()

                all_controllers_old_access_profile = []
                for i in all_checkpoints_old_access_profile:
                    all_controllers_old_access_profile.extend(
                        i.controller_set.all()
                    )
                signal_del_card = DEL_CARDS(card_number=hex_old_pass_number)
                give_signal_to_controllers(list_controllers=all_controllers_old_access_profile, signal=signal_del_card)

                all_controllers_new_access_profile = []
                for i in all_checkpoints_new_access_profile:
                    all_controllers_new_access_profile.extend(
                        i.controller_set.all()
                    )
                signal_add_card = ADD_CARD(card_number=hex_new_pass_number)
                give_signal_to_controllers(list_controllers=all_controllers_new_access_profile, signal=signal_add_card)
            if old_pass_number != new_pass_number and old_access_profile_pk == new_access_profile_pk:
                print('изменен ключ сотрудника--------------')
                hex_old_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=old_pass_number)
                hex_new_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=new_pass_number)
                all_checkpoints_select_access_profile = obj.access_profile.checkpoints.all()
                all_controllers_select_access_profile = []
                for i in all_checkpoints_select_access_profile:
                    all_controllers_select_access_profile.extend(
                        i.controller_set.all()
                    )
                signal_del_card = DEL_CARDS(card_number=hex_old_pass_number)
                give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_del_card)
                signal_add_card = ADD_CARD(card_number=hex_new_pass_number)
                give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_add_card)
            if old_pass_number == new_pass_number and old_access_profile_pk != new_access_profile_pk:
                hex_old_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=old_pass_number)
                all_checkpoints_old_access_profile = AccessProfile.objects.get(pk=old_access_profile_pk).checkpoints.all()
                all_checkpoints_new_access_profile = obj.access_profile.checkpoints.all() 
                if len(all_checkpoints_new_access_profile) > len(all_checkpoints_old_access_profile):
                    list_checkpoints_to_add_card = [el for el in all_checkpoints_new_access_profile if el not in all_checkpoints_old_access_profile]
                    list_controllers_to_add_card = []
                    for i in list_checkpoints_to_add_card:
                        list_controllers_to_add_card.extend(
                        i.controller_set.all()
                    )
                    signal_add_card = ADD_CARD(card_number=hex_old_pass_number)
                    give_signal_to_controllers(list_controllers=list_controllers_to_add_card, signal=signal_add_card)
                elif len(all_checkpoints_new_access_profile) < len(all_checkpoints_old_access_profile):
                    list_checkpoints_to_del_card = [el for el in all_checkpoints_old_access_profile if el not in all_checkpoints_new_access_profile]
                    list_controllers_to_del_card = []
                    for i in list_checkpoints_to_del_card:
                        list_controllers_to_del_card.extend(
                        i.controller_set.all()
                    )
                    signal_del_card = DEL_CARDS(card_number=hex_old_pass_number)
                    give_signal_to_controllers(list_controllers=list_controllers_to_del_card, signal=signal_del_card)
                else:
                    signal_del_card = DEL_CARDS(card_number=hex_old_pass_number)
                    signal_add_card = ADD_CARD(card_number=hex_old_pass_number)
                    list_checkpoints_to_add_card = [el for el in all_checkpoints_new_access_profile if el not in all_checkpoints_old_access_profile]
                    list_checkpoints_to_del_card = [el for el in all_checkpoints_old_access_profile if el not in all_checkpoints_new_access_profile]
                    list_controllers_to_add_card = []
                    for i in list_checkpoints_to_add_card:
                        list_controllers_to_add_card.extend(
                        i.controller_set.all()
                    )
                    list_controllers_to_del_card = []
                    for i in list_checkpoints_to_del_card:
                        list_controllers_to_del_card.extend(
                        i.controller_set.all()
                    )
                    give_signal_to_controllers(list_controllers=list_controllers_to_del_card, signal=signal_del_card)
                    give_signal_to_controllers(list_controllers=list_controllers_to_add_card, signal=signal_add_card)
        else:
            all_checkpoints_select_access_profile = obj.access_profile.checkpoints.all()
            all_controllers_select_access_profile = []
            for i in all_checkpoints_select_access_profile:
                all_controllers_select_access_profile.extend(
                    i.controller_set.all()
                )
            hex_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=form.cleaned_data["pass_number"])
            signal_add_card = ADD_CARD(card_number=hex_pass_number)
            give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_add_card)
        obj.save()
        obb = obj
        if 'microscope' in form.data:
            microscope_work_with_faces(self, request, obb, form, change)


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    
    def delete_model(self, request, obj):
        list_checkpoints_for_obj = get_all_available_passes_for_employee(obj=obj)
        list_controllers_for_obj = get_list_all_controllers_available_for_object(query_set_checkpoint=list_checkpoints_for_obj)
        card_number = obj.pass_number
        hex_card_number = validation_and_formatting_of_pass_number(card_number)

        for controller in list_controllers_for_obj:
            controller_url = controller.other_data["controller_ip"]
            serial_number = controller.serial_number
            signal_del_card = DEL_CARDS(card_number=hex_card_number)
            response = ResponseModel(message_reply=signal_del_card, serial_number_controller=serial_number)
            response_serializer = json.dumps(response)
            send_GET_request_for_controllers(url=controller_url, data=response_serializer)
        response_microscope = commands_RESTAPI_microscope(
            url=URL_API,
            login=login,
            passw=passw,
            method='get',
            point=GET_ID_FACE_MICROSCOPE.replace('<ID>', f"'{obj.pk}'"),
        )
        total_count_face_from_microscope = response_microscope['body_response']['total_count']
        if total_count_face_from_microscope != 0:
            id_microscope = response_microscope['body_response']['faces'][0]['id']
            response_microscope = commands_RESTAPI_microscope(
                url=URL_API, 
                login=login,
                passw=passw,
                method='delete',
                point=DELETE_FACE_PREF.replace('<ID>', id_microscope),
            )
            messages.success(request, f'Фото сотрудника: {obj} удалено из базы распознования лиц.')
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
    # ПЕРЕДЕЛАТЬ ПО ТИПУ РАБОТЫ С СОТРУДНИКАМИ!!!!!!!!!!!!!!!!!!!!!!!
    # ВЫНЕСТИ В МОДУЛЬ РАБОТЫ ПОДПРОГРАММ МАЙКРОСКОП!!!!!!!!!!!!!!!!
    list_display = [
        'name_departament',
        'abbreviation',
        'send_macroscope',
        'color_group',
        'interception',
        'data_departament',
    ]

    def response_post_save_add(self, request, obj):
        data_to_macroscope = {
            "external_id": "0",
            "name": "TEST3",
            "intercept": False,
            "color": "0be61600"
        }

        if 'send_macroscope' in request.POST:
            data_to_macroscope['external_id'] = obj.pk
            data_to_macroscope['name'] = request.POST['name_departament']
            data_to_macroscope['color'] = request.POST['color_group']

            if 'interception' in request.POST:
                data_to_macroscope['intercept'] = True
            resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='post', point=POST_ADD_GRP_PREF, data=data_to_macroscope)
            obj.data_departament = resp_json
            obj.save()
        return self._response_post_save(request, obj)


    def response_post_save_change(self, request, obj):
        data_to_macroscope = {
            "external_id": "0",
            "name": "TEST3",
            "intercept": False,
            "color": "0be61600"
        }

        id_group_from_microscope = obj.data_departament['id']
        point = POST_UPDATE_GRP_PREF.replace('<ID>', id_group_from_microscope)

        if 'send_macroscope' in request.POST:
            data_to_macroscope['external_id'] = obj.pk
            data_to_macroscope['name'] = request.POST['name_departament']
            data_to_macroscope['color'] = request.POST['color_group']

            if 'interception' in request.POST:
                data_to_macroscope['intercept'] = True

            resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='put', point=point, data=data_to_macroscope)
            obj.data_departament = resp_json
            obj.save()
        return self._response_post_save(request, obj)
    

    def delete_model(self, request, obj):
        try:
            id_group_from_microscope = obj.data_departament['id']
            point = POST_UPDATE_GRP_PREF.replace('<ID>', id_group_from_microscope)
            resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='delete', point=point)
        except: pass
        obj.delete()
   
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
