import json, pytz
import channels.layers

from asgiref.sync import async_to_sync


from datetime import datetime, date
 
from app_controller.models import (
    Controller
)
from app_controller.views import (
    ResponseModel
)
from app_controller.server_signals import (
    send_GET_request_for_controllers
)

from app_skud.models import (
    Staffs,  
    MonitorEvents)


def add_controller_database(message: dict, meta: dict) -> None:
    try:
        controller_type = meta["type"]
        serial_number = meta["serial_number"]
        controller_activity = message["active"]
        controller_mode = message["mode"]
        controller_ip = message['controller_ip']
        controller_url = f'http://{controller_ip}/'
    except Exception as e:
        print(f"[=ERROR=] The {e} key does not exist. Error getting key!")

    set_active = {
        "id": message['id'],
        "operation": "set_active",
        "active": 1,
        "online": 1
    }
    
    try:
        controller_obj_BD = Controller.objects.get(serial_number=serial_number)
    except:
        controller_obj_BD = None

    if controller_obj_BD == None:
        try:
            obj_for_save_DB = Controller.objects.create(
                controller_type=controller_type,
                serial_number=serial_number,
                controller_activity=controller_activity,
                controller_mode=controller_mode,
                other_data={'controller_ip': controller_url}
            )
            obj_for_save_DB.save()
            print(
                f"[=INFO=] The controller with serial number: {serial_number} saved to the database"
            )
        except Exception as e:
            print(
                f"[=ERROR=] Сontroller with serial number: {serial_number} already exists!"
            )
            print(f"[=ERROR=] The {e}!")
    else:
        print(
                f"[=INFO=] Сontroller with serial number: {serial_number} already exists!"
            )
        active = controller_obj_BD.controller_activity
        online = controller_obj_BD.controller_online
        set_active["active"] = int(active)
        set_active["online"] = int(online)
        response = ResponseModel(message_reply=set_active, serial_number_controller=meta['serial_number'])
        response_serializer = json.dumps(response)
        send_GET_request_for_controllers(url=controller_url, data=response_serializer)


def get_all_available_passes_for_employee(obj):
    try:
        return obj.access_profile.checkpoints.all()
    except Exception as e:
        print(f'[=WARNING=] The deleted employee does not have an access profile.')
        print(f'[=WARNING=] -->> {e}')
        return []


def get_list_all_controllers_available_for_object(query_set_checkpoint):
    list_all_controllers = []
    for checkpoint in query_set_checkpoint:
        gate_controllers = checkpoint.controller_set.all()
        list_all_controllers.extend(gate_controllers)
    return list_all_controllers


def add_monitor_event(message: dict, meta: dict):
    try:
        operation_type = message['operation']
    except:
        pass

    if operation_type == 'check_access':
        granted = add_check_access_in_monitor_event(message=message, meta=meta)
        return granted
    elif operation_type == 'events':
        add_events_in_monitor_event(message=message, meta=meta)
    else:
        pass


def add_check_access_in_monitor_event(message: dict, meta: dict) -> int:
    tz = pytz.timezone('Etc/GMT-6') # это в конфиг файл
    date_time_created = datetime.now(tz=tz)
    date_time_created = date_time_created.strftime("%Y-%m-%d %H:%M:%S")
    try:
        staff = Staffs.objects.get(pass_number=message['card'])
        try:
            photo = staff.employee_photo.url
        except Exception as e:
            photo = None
            print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')
        staff_last_name = staff.last_name
        staff_first_name = staff.first_name
        departament = staff.department.name_departament
    except Exception as e:
        print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')
        staff = photo = staff_last_name = staff_first_name = departament = None
    try:
        controller = Controller.objects.get(serial_number=meta["serial_number"])
        checkpoint = controller.checkpoint
        serial_number = controller.serial_number
    except Exception as e:
        controller = checkpoint = serial_number = None
        print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')

    granted = give_issue_permission(staff=staff, checkpoint=checkpoint)

    obj_for_BD = MonitorEvents(
        operation_type = message['operation'],
        time_created = date_time_created,
        card = message['card'],
        staff = staff,
        controller = controller,
        checkpoint = checkpoint,
        granted = granted,
        event = None, # HARDCODE
        flag = None, # HARDCODE
        data_monitor_events = message
    )
    obj_for_BD.save()

    # ==============================================================
    data_for_sending_sockets = {
        'time_created': date_time_created,
        'card': message['card'],
        'photo': photo,
        'staff_last_name': staff_last_name,
        'staff_first_name': staff_first_name,
        'departament': departament,
        'controller': serial_number,
        'checkpoint': str(checkpoint),
        'granted': granted,
    }
    try:
        channels_ = channels.layers.get_channel_layer()
        async_to_sync(channels_.group_send)("client", {"type": "receive", "text_data": data_for_sending_sockets})
    except Exception as e:
        print(f'[=INFO=] Page with WebSocket not running!')
        print(f'[=ERROR=] {e}')
    # ==============================================================
    return granted


def add_events_in_monitor_event(message: dict, meta: dict):
    granted_0 = [2, 4, 6, 7, 14, 17, 26, 28, 30]
    try:
        operation_type = message['operation']
    except:
        pass
    try:
        controller = Controller.objects.get(serial_number=meta["serial_number"])
        checkpoint = controller.checkpoint
    except:
        print(
            f'[=WARNING=] The server receives a signal EVENTS from an unknown controller: {meta["serial_number"]}'
        )
        controller = None
        checkpoint = None
    try:
        list_events = message["events"]
        batch_size = len(list_events)
    except Exception as e:
        print(f"[=ERROR=] Failed to get list of events!")
        print(f"[=ERROR=] The {e}!")
    
    objs_for_save_BD = []
    for event in list_events:
        try:
            staff = Staffs.objects.get(pass_number=event["card"])
            employee_photo = f'/media/{str(staff.employee_photo)}'
            last_name = staff.last_name
            first_name = staff.first_name
            department = str(staff.department)
        except:
            print(f'[=WARNING=] Event with unknown card number: {event["card"]}')
            employee_photo = None 
            last_name = None
            first_name = None
            department = None 
            staff = None
            
        try:
            if event['event'] in granted_0:
                granted = 0
            else: 
                granted = 1
            objs_for_save_BD.append(
                MonitorEvents(
                    operation_type = operation_type,
                    time_created = event['time'],
                    card = event['card'],
                    staff = staff,
                    controller = controller,
                    checkpoint = checkpoint,
                    granted = granted,
                    event = event['event'],
                    flag = event['flag'],
                    data_monitor_events = message
                )
            )
        except:
            pass

    data_for_sending_sockets = {
        'time_created': event['time'],
        'card': event['card'],
        'photo': employee_photo,
        'staff_last_name': last_name,
        'staff_first_name': first_name,
        'departament': department,
        'controller': str(controller),
        'checkpoint': str(checkpoint),
        'granted': granted,
    }
    try:
        channels_ = channels.layers.get_channel_layer()
        async_to_sync(channels_.group_send)("client", {"type": "receive", "text_data": data_for_sending_sockets})
    except Exception as e:
        print(f'[=INFO=] Page with WebSocket not running!')
        print(f'[=ERROR=] {e}')

    MonitorEvents.objects.bulk_create(objs=objs_for_save_BD, batch_size=batch_size)


def give_issue_permission(staff = None, checkpoint = None):
    if staff == None or checkpoint == None:
        return 0
    try:
        accessible_gates = staff.access_profile.checkpoints.all()
    except Exception as e:
        print(f'[=WARNING=] Employee: {staff} does not have an access profile set.')
        print(f'[=WARNING=] Exception: {e}.')
        return 0

    if checkpoint in accessible_gates:
        return 1
    return 0


def get_events_for_range_dates(start_date: tuple, end_date: tuple):
    start_date = date(*start_date)
    end_date = date(*end_date)
    obj_BD_date_filter = MonitorEvents.objects.filter(
        time_created__range=(start_date, end_date)
    )
    return obj_BD_date_filter
