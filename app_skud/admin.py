import json

from core.settings import env

from django.shortcuts import render, redirect
from django.urls import re_path
from django.contrib import messages

from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models

from rangefilter.filters import (
    DateRangeFilterBuilder,
    DateTimeRangeFilterBuilder,
    NumericRangeFilterBuilder,
    DateRangeQuickSelectListFilterBuilder,
)

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
    get_events_for_range_dates, get_events_by_days,
    get_all_staffs_from_cache
)

from app_controller.server_signals import (
    ADD_CARD,
    DEL_CARDS,
    send_GET_request_for_controllers, 
    async_send_GET_request_for_controllers
)

from .f_export_from_DB import import_data_from_database, import_tabel_from_database

from app_skud.utils_to_microscope import (
    URL_API, POST_ADD_GRP_PREF, POST_UPDATE_GRP_PREF,
    login, passw, DELETE_FACE_PREF, GET_ID_FACE_MICROSCOPE,
    GET_GRP_TO_EXTERNAL_ID,
    commands_RESTAPI_microscope, microscope_work_with_faces
    )

from app_controller.views import ResponseModel

from app_skud.utilities import (
    validation_and_formatting_of_pass_number, give_signal_to_controllers,
    validation_and_formatting_of_pass_number_form,
    work_with_controllers_when_an_employee_data_changes)


ACCESS_PROFILE_LIST = [
    'name_access_profile',
    'description_access_profile',
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

from django.core.cache import cache
from app_skud.forms import StaffsModelForm

@admin.register(Staffs)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'patronymic',
        'phone_number', 'department', 'position',
        'access_profile', 'pass_number', 'get_image', 'face_detect'
    ]
    list_filter = ['department', 'position', 'access_profile']
    search_fields = ['last_name__istartswith', 'first_name__istartswith', 'patronymic__istartswith', 'pass_number__startswith']
    form = StaffsModelForm
    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }
    fieldsets = (
        (None, {'fields': (('employee_photo', 'pass_number'), 'microscope')}),
        ('ФИО', {'fields': (('last_name', 'first_name', 'patronymic'),)}),
        ('Контакты', {'fields': (('phone_number', 'home_address'),)}),
        ('Транспорт', {'fields': (('car_number', 'car_model'),)}),
        ('Рабочие данные', {'fields': (('department', 'position'),)}),
        ('Профили', {'fields': (('access_profile', 'time_profale'),)}),
    )
    
 
    def face_detect(self, obj):
        try:
            microscope = obj.data_staffs['microscope']
        except:
            microscope = False
        if microscope:
            return mark_safe(f'<img src="/media/galka.png" width="50" height="50"')
        else:
            return mark_safe(f'<img src="/media/krest.png" width="50" height="50"')
    face_detect.short_description = 'РАСПОЗНОВАНИЕ ЛИЦ'


    def get_image(self, obj):
        if obj.employee_photo:
            return mark_safe(f'<img src={obj.employee_photo.url} width="50" height="50"')
        else:
            return None
    get_image.short_description = 'ФОТО'

 
    def save_model(self, request, obj, form, change):
        resp_status = []
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
                resp_status = give_signal_to_controllers(list_controllers=all_controllers_old_access_profile, signal=signal_del_card)

                all_controllers_new_access_profile = []
                for i in all_checkpoints_new_access_profile:
                    all_controllers_new_access_profile.extend(
                        i.controller_set.all()
                    )
                signal_add_card = ADD_CARD(card_number=hex_new_pass_number)
                resp_status = give_signal_to_controllers(list_controllers=all_controllers_new_access_profile, signal=signal_add_card)
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
                resp_status = give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_del_card)
                signal_add_card = ADD_CARD(card_number=hex_new_pass_number)
                resp_status = give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_add_card)
            if old_pass_number == new_pass_number and old_access_profile_pk != new_access_profile_pk:
                print('изменен профиль сотрудника--------------')
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
                    resp_status = give_signal_to_controllers(list_controllers=list_controllers_to_add_card, signal=signal_add_card)
                elif len(all_checkpoints_new_access_profile) < len(all_checkpoints_old_access_profile):
                    list_checkpoints_to_del_card = [el for el in all_checkpoints_old_access_profile if el not in all_checkpoints_new_access_profile]
                    list_controllers_to_del_card = []
                    for i in list_checkpoints_to_del_card:
                        list_controllers_to_del_card.extend(
                        i.controller_set.all()
                    )
                    signal_del_card = DEL_CARDS(card_number=hex_old_pass_number)
                    resp_status = give_signal_to_controllers(list_controllers=list_controllers_to_del_card, signal=signal_del_card)
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
                    resp_status = give_signal_to_controllers(list_controllers=list_controllers_to_del_card, signal=signal_del_card)
                    resp_status = give_signal_to_controllers(list_controllers=list_controllers_to_add_card, signal=signal_add_card)
        else:
            all_checkpoints_select_access_profile = obj.access_profile.checkpoints.all()
            all_controllers_select_access_profile = []
            for i in all_checkpoints_select_access_profile:
                all_controllers_select_access_profile.extend(
                    i.controller_set.all()
                )
            hex_pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=form.cleaned_data["pass_number"])
            signal_add_card = ADD_CARD(card_number=hex_pass_number)
            resp_status = give_signal_to_controllers(list_controllers=all_controllers_select_access_profile, signal=signal_add_card)
        if len(resp_status) != 0:
            for el in resp_status:
                messages.set_level(request=request, level=messages.ERROR)
                messages.error(request=request, message=el)
            return None
        else:
            obj.save()
            obb = obj
        if 'microscope' in form.data:
            microscope_work_with_faces(self, request, obb, form, change)
        all_staffs = Staffs.objects.all()
        cache.set('all_staffs', all_staffs, timeout=3600)


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
        list_errors = []
        for controller in list_controllers_for_obj:
            controller_url = controller.other_data["controller_ip"]
            serial_number = controller.serial_number
            signal_del_card = DEL_CARDS(card_number=hex_card_number)
            response = ResponseModel(message_reply=signal_del_card, serial_number_controller=serial_number)
            response_serializer = json.dumps(response)
            resp_status = send_GET_request_for_controllers(url=controller_url, data=response_serializer)
            if resp_status != None:
                list_errors.append(resp_status)
        if len(list_errors) != 0:
            for el in list_errors:
                messages.set_level(request=request, level=messages.ERROR)
                messages.error(request=request, message=el)
            return None
        else:
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
            all_staffs = Staffs.objects.all()
            cache.set('all_staffs', all_staffs, timeout=3600)

        
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
            try:
                controller = Controller.objects.get(checkpoint=checpoint)
                controller_list_this_access_profile.append(controller)
            except:
                continue
        signal_del_cards = DEL_CARDS(card_number=list_pass_number_access_profile)
        for el in controller_list_this_access_profile:
            send_GET_request_for_controllers(url=el.other_data['controller_ip'],
                                             data=json.dumps(ResponseModel(message_reply=signal_del_cards,
                                                                           serial_number_controller=el.serial_number))
            )
        obj.delete()


from django.utils.translation import gettext_lazy as _
class FilterTypeEvent(admin.SimpleListFilter):
    title = _('Тип события')
    parameter_name = 'operation_type'

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ('check_access', _('Двуфакторный')),
            ('events', _('Однофакторный')),
        )

    def queryset(self, request, queryset):
        # apply the filter to the queryset
        if self.value() == 'check_access':
            return queryset.filter(operation_type='check_access')
        if self.value() == 'events':
            return queryset.filter(operation_type='events')
        

class FilterGranted(admin.SimpleListFilter):
    title = _('Вердикт события')
    parameter_name = 'granted'

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ('0', _('Доступ Запрещен')),
            ('1', _('Доступ Разрешен')),
        )

    def queryset(self, request, queryset):
        # apply the filter to the queryset
        if self.value() == '0':
            return queryset.filter(granted='0')
        if self.value() == '1':
            return queryset.filter(granted='1')


from .forms import MonitorEventsModelForm, MonitorEventsTabelModelForm
@admin.register(MonitorEvents)
class MonitorEventsAdmin(admin.ModelAdmin):
    list_display = [
        'get_id_event',
        'time_created',
        'staff',
        # 'get_department',
        'checkpoint',
        'get_direct',
        # 'get_late_status',
    ]
    list_filter = (
        ('time_created', DateRangeQuickSelectListFilterBuilder()),
        FilterTypeEvent,
        'checkpoint',
        FilterGranted,
        # 'event',
        # 'flag',
    )
    search_fields = ['time_created__istartswith', 'staff__istartswith', 'staff__iexact', 'staff__icontains' ]
    actions = ['delete_selected',]

    change_list_template = 'app_skud/admin/monitorevents_change_list.html'

    def get_urls(self):
        urls = super(MonitorEventsAdmin, self).get_urls()
        custom_urls = [
            re_path('^import/$', self.date_range_view_function, name='process_import'),
            re_path('^tabel/$', self.get_timesheets_of_employees, name='tabel'),]
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

        site_header = 'Система Контроля и Управления Доступом'
        return render(request, 'app_skud/admin/unloading_events.html', context={'form': form, 'site_header': site_header})
    

    def get_timesheets_of_employees(self, request):
        pass
        form = MonitorEventsTabelModelForm(request.POST)

        if request.method == 'POST':
            if form.is_valid():
                staff = form.data['staff']
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

                events_by_days = get_events_by_days(qs=obj_BD_date_filter)
                
                # date_obj_start_date_for_filter = date(*start_date_for_filter)
                # date_obj_end_date_for_filter = date(*end_date_for_filter)
                # result = abs(date_obj_end_date_for_filter - date_obj_start_date_for_filter)


                return import_tabel_from_database(request=request, data=events_by_days)
        site_header = 'Система Контроля и Управления Доступом'
        return render(request, 'app_skud/admin/unloading_events.html', context={'form': form, 'site_header': site_header})

    # def get_department(self, obj):
    #     return mark_safe(f'{obj.data_monitor_events["dep"]}')
    # get_department.short_description = 'Департамент'

    def get_late_status(self, obj):
        try:
            return obj.data_monitor_events["late_status"]
        except:
            return ' --- '
    get_late_status.short_description = 'Статус опоздания'


    def get_direct(self, obj):
        try:
            direct = obj.data_monitor_events["direct"]
            if direct == 1 or direct == 'Вход':
                return mark_safe(f'Вход')
            else: 
                return mark_safe(f'Выход')
        except:
            direct = ' --- '
    get_direct.short_description = 'Направление'

    # def get_granted(self, obj):
    #     if obj.granted == '1':
    #         return mark_safe(f'Доступ разрещен')
    #     else:
    #         return mark_safe(f'Доступ запрещен')
    # get_granted.short_description = 'Разрешение'

    def get_id_event(self, obj):
        return mark_safe(f'{obj.pk}')
    get_id_event.short_description = '№ п/п'

    # def get_type_auten(self, obj):
    #     if obj.operation_type == 'check_access':
    #         return mark_safe(f'Двухфакторная аутентификация')
    #     else:
    #         return mark_safe(f'Однофакторная аутентификация')
    # get_type_auten.short_description = 'Тип аутентификация'
    

from django.urls import re_path, reverse
from django.utils.html import format_html

@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ['name_checkpoint',
                    'description_checkpoint',
                    ]+['account_actions']
    actions = ['delete_selected',]

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'monitor/(?P<serial_number_ch>.+)$',
                self.admin_site.admin_view(self.checkpoint_monitor),
                name='checkpoint_monitor',
            ),
        ]
        return custom_urls + urls


    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">МОНИТОР</a> ',
            reverse('admin:checkpoint_monitor', args=[obj.pk]),
        )
    account_actions.short_description = 'Мониторы проходных'
    account_actions.allow_tags = True

    def checkpoint_monitor(self, request, *args, **kwargs):
        # TO DO есть ошибка kwargs['serial_number_ch'] иногда null
        try:
            checkpoint = Checkpoint.objects.get(pk=kwargs['serial_number_ch'])
            controllers = checkpoint.controller_set.all()
            print(f'----checkpoint---->>> {checkpoint} === {type(checkpoint)}')
            perimetr_observer = checkpoint.perimetermonitor_set.all()

            print(f'----p---->>> {perimetr_observer} === {type(perimetr_observer)}')
            return render(request, 'app_skud/checkpoint_detail.html', context={
                'pk_checkpoint': kwargs['serial_number_ch'],
                'checkpoint': checkpoint,
                'controllers': controllers, 
                'perimetr_observer': perimetr_observer,
                'perimetr_observer_count': perimetr_observer[0].perimeter_counter if len(perimetr_observer) != 0 else [] 
            })
        except ValueError:
            pass
        except UnboundLocalError:
            pass


@admin.register(Department)
class DepartamenAdmin(admin.ModelAdmin):
    list_display = [
        'name_departament',
        'abbreviation',
        'send_macroscope',
        'color_group',
        'interception',
        # 'data_departament',
    ]

   
    def save_model(self, request, obj, form, change):
        obj.save()
        macroscope = env("MACROSCOPE")
        if macroscope == '1' and bool(form.data.get('send_macroscope')):
            try:
                if obj.send_macroscope:
                    data_to_macroscope = {
                        "external_id": obj.pk,
                        "name": obj.name_departament,
                        "intercept": obj.interception,
                        "color": obj.color_group
                    }
                if not change:
                    resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='post', point=POST_ADD_GRP_PREF, data=data_to_macroscope)
                else:
                    entrypoint = f"{GET_GRP_TO_EXTERNAL_ID}'{obj.pk}'"
                    resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='get', point=entrypoint, data=data_to_macroscope)
                    
                    if len(resp_json['body_response']['groups']) != 0:
                        id_group_macroscope = resp_json['body_response']['groups'][0]['id']
                        point = POST_UPDATE_GRP_PREF.replace('<ID>', id_group_macroscope)
                        resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='put', point=point, data=data_to_macroscope)
                
                obj.data_departament = resp_json
                obj.save()
            except Exception as e:
                messages.set_level(request=request, level=messages.ERROR)
                messages.error(request=request, message=f'Не удалось сохранить {obj}, причина: {e}')
        else: 
            pass


    def delete_model(self, request, obj):
        macroscope = env("MACROSCOPE")
        if macroscope == '1':
            try:
                entrypoint = f"{GET_GRP_TO_EXTERNAL_ID}'{obj.pk}'"
                resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='get', point=entrypoint)
                if len(resp_json['body_response']['groups']) != 0:
                    id_group_macroscope = resp_json['body_response']['groups'][0]['id']
                    point = POST_UPDATE_GRP_PREF.replace('<ID>', id_group_macroscope)
                    resp_json = commands_RESTAPI_microscope(url=URL_API, login=login, passw=passw, method='delete', point=point)
                obj.delete()
            except Exception as e:
                messages.set_level(request=request, level=messages.ERROR)
                messages.error(request=request, message=f'Не удалось удалить {obj}, причина: {e}')
        else: obj.delete()
   
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
