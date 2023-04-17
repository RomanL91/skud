import json
import requests

from django.contrib import admin
from django.db.models import Q
from django.urls import re_path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect

from .models import Controller
from .views import ResponseModel
from .server_signals import (
    SET_ACTIVE, SET_MODE, 
    send_GET_request_for_controllers,
    READ_CARDS
)
from app_skud.forms import StaffsModelForm
from app_skud.models import Staffs
from .tests import MOCK_READ_CARDS


controller_list_display = [
        'controller_type',
        'serial_number',
        'controller_activity',
        'controller_online',
        'controller_mode',
        'checkpoint',
    ]


@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_filter = controller_list_display
    list_display = controller_list_display+['account_actions']
    readonly_fields = ['serial_number',]

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)


    def response_post_save_change(self, request, obj):
        controller_url = obj.other_data["controller_ip"]
        serial_num_controller = obj.serial_number
        send_data = dict(request.POST)
        set_active = SET_ACTIVE(send_data=send_data)  
        set_mode = SET_MODE(send_data=send_data)  
        resp = [set_active, set_mode]  
        resonse = ResponseModel(message_reply=resp, serial_number_controller=serial_num_controller)  
        response_serializer = json.dumps(resonse)
        send_GET_request_for_controllers(url=controller_url ,data=response_serializer)
        return self._response_post_save(request, obj)


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<serial_number>.+)/unload_cards/$',
                self.admin_site.admin_view(self.unload_cards),
                name='unload_cards',
            ),
            re_path(
                r'^(?P<serial_number>.+)/delete_cards/$',
                self.admin_site.admin_view(self.delete_cards),
                name='delete_cards',
            ),
        ]
        return custom_urls + urls


    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Получить карты</a> '
            '<a class="button" href="{}">##Удалить карты##</a>',
            reverse('admin:unload_cards', args=[obj.serial_number]),
            reverse('admin:delete_cards', args=[obj.serial_number]),
        )
    account_actions.short_description = 'Действия с контроллером'
    account_actions.allow_tags = True


    # нужна оптимизация, возможно поискового запроса и точно [if request.method == 'POST'] блока
    def unload_cards(self, request, *args, **kwargs):
        form = StaffsModelForm(request.POST)
        # 1-обращаюсь к БД, достаю контроллер по серийнику, из поля достаю его IP
        try:
            controller = Controller.objects.get(serial_number=kwargs['serial_number'])
            IP_adress = controller.other_data['controller_ip']
        except: 
            pass
        # 2-создаю модель запроса, преобразую в json, отправляю запрос, вывожу возможные ошибки(если есть, редирект)
        try:
            read_cards = READ_CARDS()
            request_for_controllers = ResponseModel(message_reply=read_cards, serial_number_controller=int(kwargs['serial_number']))
            response_serializer = json.dumps(request_for_controllers)
            response_for_controllers = requests.get(url=IP_adress, data=response_serializer).json()
        except Exception as e:
            print(f"[=ERROR=] Sending failed! \n[=ERROR=]: {e}")
            self.message_user(request=request, message=f'Управляющий контроллером: {controller} сервер не доступен. URL: {IP_adress}', level='error')
            return redirect(to=request.META["HTTP_REFERER"])
        # 3-обрабатываю сообщение от контроллера и формирую из него список карт вида: ['000000678D58', '0000006FFE8E', ...]
        # response_for_controllers = MOCK_READ_CARDS
        list_masseges = response_for_controllers['messages']
        for msg in list_masseges:
            try:
                list_cards = msg['cards']
            except:
                list_cards = None
                continue
        if list_cards != None:
            list_num_cards_from_controller = [num_card['card'] for num_card in list_cards]
        # 4-обращаюсь к БД, достаю все сущности сотрудников у которых номер карты есть в списке сформированным ранее
        staffs_in_BD = Staffs.objects.filter(pass_number__in=list_num_cards_from_controller)
            # ситуация: в контроллере карта есть а в БД нет:
        list_cards_staffs_from_BD = [i.pass_number for i in staffs_in_BD] 
        list_num_cards_from_controller_set = set(list_num_cards_from_controller)
        list_cards_staffs_from_BD_set = set(list_cards_staffs_from_BD)
        if list_num_cards_from_controller_set != list_cards_staffs_from_BD_set:
            differents = list_num_cards_from_controller_set - list_cards_staffs_from_BD_set
        else: differents = None
        # 5-рендарим это
        if request.method == 'POST':
            data_for_search = {}
            for i in form.data:
                if i != 'csrfmiddlewaretoken':
                    if form.data[i] != '':
                        data_for_search.setdefault(i, form.data[i])
                    data_for_search.setdefault(i, None)
            staffs_in_BD_ = Staffs.objects.filter(
                Q(last_name=data_for_search['last_name']) 
                | Q(first_name=data_for_search['first_name']) 
                | Q(phone_number=data_for_search['phone_number']) 
                | Q(pass_number=data_for_search['pass_number'])
            )
                # стоит пересмотреть подхо к поиску и включить возможность показа дожностей и департаментом, усложнить фильтрационный запрос
                # (Q(department=data_for_search['department']) | Q(position=data_for_search['position'])) | (Q(last_name=data_for_search['last_name']) | Q(first_name=data_for_search['first_name']) | Q(phone_number=data_for_search['phone_number']) | Q(pass_number=data_for_search['pass_number'])))
            try:
                staff_cards_from_form = [i.pass_number for i in staffs_in_BD_][-1] 
            except IndexError:
                staff_cards_from_form = None
            if len(staffs_in_BD_) != 0 and staff_cards_from_form in list_cards_staffs_from_BD_set:
                return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD_, 'differents': differents, 'serial_number': kwargs['serial_number']})
            else:
                return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD, 'differents': differents, 'serial_number': kwargs['serial_number']})
        return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD, 'differents': differents, 'serial_number': kwargs['serial_number']})


    def delete_cards(self, request, *args, **kwargs):
        print('delete_cards <<<<<<<<<<<------------')
        print(f'args ---->>> {args}')
        print(f'kwargs ---->>> {kwargs}')


admin.site.site_header = 'Система Контроля Удаленным Доступом'
admin.site.index_title = ''                 # default: "Site administration"
admin.site.site_title = 'СКУД'    # default: "Django site admin"
admin.site.site_url = None   
admin.site.disable_action('delete_selected')
