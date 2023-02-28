from django.contrib import admin

from .models import Controller, Event

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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = event_list_display
    list_filter = event_list_display


admin.site.site_header = 'ADMIN'                    # default: "Django Administration"
admin.site.index_title = ''                 # default: "Site administration"
admin.site.site_title = 'ADMIN'    # default: "Django site admin"
admin.site.site_url = None   
# admin.site.index_template = '/home/romanl/skud/app_controller/templates/app_controller/root.html'   


# class MyModelAdmin(admin.ModelAdmin):
#     class Media:
#         css = {
#             'all': ('/home/romanl/skud/style.ccs',)
#         }
