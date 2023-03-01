import json
from django.contrib import admin

from .models import Controller, Event
from .views import ResponseModel
from .server_signals import (
    URL,
    SET_ACTIVE, SET_MODE, 
    send_GET_request_for_controllers
)

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

event_list_display = [
        'event',
        'card',
        'time',
        'flag',
        'data_event',
        'controller',
        'event_initiator',
    ]

@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = controller_list_display
    list_filter = controller_list_display

    def response_post_save_change(self, request, obj):
        serial_num_controller = request.POST['serial_number']
        send_data = dict(request.POST)
        set_active = SET_ACTIVE(send_data=send_data)  
        set_mode = SET_MODE(send_data=send_data)  
        resp = [set_active, set_mode]  
        resonse = ResponseModel(message_reply=resp, serial_number_controller=serial_num_controller)  
        response_serializer = json.dumps(resonse)
        send_GET_request_for_controllers(url=URL ,data=response_serializer)
        return self._response_post_save(request, obj)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = event_list_display
    list_filter = event_list_display


admin.site.site_header = 'ADMIN'                    # default: "Django Administration"
admin.site.index_title = ''                 # default: "Site administration"
admin.site.site_title = 'ADMIN'    # default: "Django site admin"
admin.site.site_url = None   
