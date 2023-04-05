import json
import requests

from django.contrib import admin
from django.db.models import Q
from django.urls import re_path
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import render


from .models import Controller
from .views import ResponseModel
from .server_signals import (
    SET_ACTIVE, SET_MODE, 
    send_GET_request_for_controllers,
    READ_CARDS
)
from app_skud.forms import StaffsModelForm
from app_skud.models import Staffs

MOCK = {
    'type': 'z5r net 8000',
    'sn': 4225,
    'messages': [
        {
            'cards': [
                {
                    'card': '0000006FFE8E',
                    'pos': 0,
                    'flags': 0,
                    'Key.fErased': 0,
                    'tz': 255
                },
                {
                    'card': '0000006FFE8D',
                    'pos': 0,
                    'flags': 0,
                    'Key.fErased': 0,
                    'tz': 255
                },
                # {
                #     'card': '0000006FF000',
                #     'pos': 0,
                #     'flags': 0,
                #     'Key.fErased': 0,
                #     'tz': 255
                # },
                # {
                #     'card': '0000006FF001',
                #     'pos': 0,
                #     'flags': 0,
                #     'Key.fErased': 0,
                #     'tz': 255
                # }
            ]
        }
    ]
}

controller_list_display = [
        'controller_type',
        'serial_number',
        'controller_activity',
        'controller_online',
        'controller_mode',
        'checkpoint',
        'data_settings_zone',
        'other_data',
    ]


@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = [
        'controller_type',
        'serial_number',
        'account_actions',
        'controller_activity',
        'controller_online',
        'controller_mode',
        'checkpoint',
        # 'data_settings_zone',
        # 'other_data',
    ]
    list_filter = controller_list_display
    # list_editable = [ 
    #     'controller_activity',
    #     'controller_online',
    #     'controller_mode',
    #     'checkpoint',
    # ]
    readonly_fields = (
        'id',
        'controller_type',
        'account_actions',
    )
    # actions = ['account_actions',]
    # change_list_template = 'app_controller/admin/controller_change_list.html'


    def response_post_save_change(self, request, obj):
        controller_url = obj.other_data["controller_ip"]
        serial_num_controller = int(request.POST['serial_number'])
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
        print('def account_actions')
        print(f'obj --->>> {obj}')
        print(f'obj.serial_number --->>> {obj.serial_number}')
        return format_html(
            '<a class="button" href="{}">Получить карты</a> '
            '<a class="button" href="{}">Удалить карты</a>',
            reverse('admin:unload_cards', args=[obj.serial_number]),
            reverse('admin:delete_cards', args=[obj.serial_number]),
        )
    account_actions.short_description = 'Действия с контроллером'
    account_actions.allow_tags = True


    def unload_cards(self, request, *args, **kwargs):
        form = StaffsModelForm(request.POST)
        print(f'kwargs ---->>> {kwargs}')
        # ===================================================================================
        # 1-обращаюсь к БД, достаю контроллер по серийнику, из поля достаю его IP
        # 2-выполняю get запрос и получаю ответ(response_controller_read_card) в виде MOCK
        # 3-обрабатываю МОСК и формирую из него про список карт вида: ['000000678D58', '0000006FFE8E', ...]
        # 4-обращаюсь к БД, достаю все сущности сотрудников у которых номер карты есть в списке сформированным ранее
        #       Staffs.objects.filter(pass_number__in=[v1,v2])
        # 5-рендарим это

        # 1
        try:
            controller = Controller.objects.get(serial_number=kwargs['serial_number'])
            IP_adress = controller.other_data['controller_ip']
            print(IP_adress)
        except: 
            pass
        # 2
        # try:
        #     read_cards = READ_CARDS()
        #     request_for_controllers = ResponseModel(message_reply=read_cards, serial_number_controller=int(kwargs['serial_number']))
        #     print(f'request_for_controllers ---->>> {request_for_controllers}')
        #     response_serializer = json.dumps(request_for_controllers)
        #     response_for_controllers = requests.get(url=IP_adress, data=response_serializer)
        #     print(f'response_for_controllers ---->>> {response_for_controllers.json()}')
        # except:
        #     pass
        # 3-обработка МОСК
        response_controller_read_card = MOCK #это заглушка, типа получил карты от контроллера
        # response_controller_read_card = response_for_controllers.json() #это заглушка, типа получил карты от контроллера
        list_masseges = response_controller_read_card['messages']
        for msg in list_masseges:
            try:
                list_cards = msg['cards']
            except:
                list_cards = None
                continue
        if list_cards != None:
            list_num_cards_from_controller = [num_card['card'] for num_card in list_cards]
        else: pass
        # 4-обращаюсь к БД, достаю все сущности сотрудников
        staffs_in_BD = Staffs.objects.filter(pass_number__in=list_num_cards_from_controller)
        # ситуация: в контроллере карта есть а в БД нет:
        list_cards_staffs_from_BD = [i.pass_number for i in staffs_in_BD] 
        list_num_cards_from_controller_set = set(list_num_cards_from_controller)
        list_cards_staffs_from_BD_set = set(list_cards_staffs_from_BD)
        if list_num_cards_from_controller_set != list_cards_staffs_from_BD_set:
            differents = list_num_cards_from_controller_set - list_cards_staffs_from_BD_set
        # ===================================================================================
        # ДУБЛИРОВАНИЕ ------->>>>>>
            if request.method == 'POST':
                data_for_search = {}
                for i in form.data:
                    if i != 'csrfmiddlewaretoken':
                        if form.data[i] != '':
                            data_for_search.setdefault(i, form.data[i])
                        data_for_search.setdefault(i, None)
                staffs_in_BD_ = Staffs.objects.filter(
                    Q(last_name=data_for_search['last_name']) | Q(first_name=data_for_search['first_name']) | Q(phone_number=data_for_search['phone_number']) | Q(pass_number=data_for_search['pass_number']))
                    # (Q(department=data_for_search['department']) | Q(position=data_for_search['position'])) | (Q(last_name=data_for_search['last_name']) | Q(first_name=data_for_search['first_name']) | Q(phone_number=data_for_search['phone_number']) | Q(pass_number=data_for_search['pass_number'])))
                if len(staffs_in_BD_) != 0:
                    return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD_, 'differents': differents})
                return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD, 'differents': differents})
            return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD, 'differents': differents})
        
        if request.method == 'POST':
            data_for_search = {}
            for i in form.data:
                if i != 'csrfmiddlewaretoken':
                    if form.data[i] != '':
                        data_for_search.setdefault(i, form.data[i])
                    data_for_search.setdefault(i, None)
            staffs_in_BD_ = Staffs.objects.filter(
                Q(last_name=data_for_search['last_name']) | Q(first_name=data_for_search['first_name']) | Q(phone_number=data_for_search['phone_number']) | Q(pass_number=data_for_search['pass_number']))
                # (Q(department=data_for_search['department']) | Q(position=data_for_search['position'])) | (Q(last_name=data_for_search['last_name']) | Q(first_name=data_for_search['first_name']) | Q(phone_number=data_for_search['phone_number']) | Q(pass_number=data_for_search['pass_number'])))
            if len(staffs_in_BD_) != 0:
                return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD_})
            return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD})
        return render(request, 'app_controller/admin/unloading_cards.html', context={'form': form, 'staffs': staffs_in_BD})


    def delete_cards(self, request, *args, **kwargs):
        print('delete_cards <<<<<<<<<<<------------')
        print(f'args ---->>> {args}')
        print(f'kwargs ---->>> {kwargs}')





admin.site.site_header = 'ADMIN'                    # default: "Django Administration"
admin.site.index_title = ''                 # default: "Site administration"
admin.site.site_title = 'ADMIN'    # default: "Django site admin"
admin.site.site_url = None   
admin.site.disable_action('delete_selected')
