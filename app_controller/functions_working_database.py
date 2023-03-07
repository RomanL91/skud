import json, datetime, uuid

from app_controller.models import (
    Controller, Event
)
from app_controller.views import ResponseModel
from app_controller.server_signals import (
    URL,
    send_GET_request_for_controllers
)

from app_skud.models import (
    Staffs, MonitorCheckAccess, 
    MonitorEvents
)
from app_skud.consumers import MySyncConsumer # MyAsyncConsumer 

# реалиация на синхронном варианте
socket = MySyncConsumer()


def add_controller_database(message: dict, meta: dict) -> None:
    try:
        controller_type = meta["type"]
        serial_number = meta["serial_number"]
        controller_activity = message["active"]
        controller_mode = message["mode"]
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
        send_GET_request_for_controllers(url=URL, data=response_serializer)


def add_events_database(message: dict, meta: dict) -> None:
    try:
        controller_ = Controller.objects.get(serial_number=meta["serial_number"])
    except:
        print(
            f'[=WARNING=] The server receives a signal EVENTS from an unknown controller: {meta["serial_number"]}'
        )
        controller_ = None
    try:
        list_events = message["events"]
        batch_size = len(list_events)
    except Exception as e:
        print(f"[=ERROR=] Failed to get list of events!")
        print(f"[=ERROR=] The {e}!")

    objs_for_save_BD = []
    for event_ in list_events:
        try:
            staff_ = Staffs.objects.get(pass_number=event_["card"])
        except:
            print(f'[=WARNING=] Event with unknown card number: {event_["card"]}')
            staff_ = None
        try:
            objs_for_save_BD.append(
                Event(
                    event=event_["event"],
                    card=event_["card"],
                    time=event_["time"],
                    flag=event_["flag"],
                    data_event=event_,
                    controller=controller_,
                    event_initiator=staff_,
                )
            )
        except:
            pass  # что-то при ошибках append и создание ленивых данных модели
    Event.objects.bulk_create(objs=objs_for_save_BD, batch_size=batch_size)


def add_access_check_database_and_issue_permission(message: dict, meta: dict) -> dict:
    try:
        num_card = message["card"]
        controller_serial_num = meta["serial_number"]
    except:
        num_card = None  # HARCODE !!!!!!!!!
        controller_serial_num = None  # HARCODE !!!!!!!!!
    try:
        staff = Staffs.objects.get(pass_number=num_card)
        departament = staff.department
        accessible_gates = staff.access_profile.checkpoints.all()
    except:
        staff = None  # HARCODE !!!!!!!!!
        departament = None  # HARCODE !!!!!!!!!
        accessible_gates = None  # HARCODE !!!!!!!!!
    try:
        controller = Controller.objects.get(serial_number=controller_serial_num)
        checkpoint = controller.checkpoint
    except:
        controller = None  # HARCODE !!!!!!!!!
        checkpoint = None  # HARCODE !!!!!!!!!

    data_monitor = {
        "num_card": str(num_card),
        "controller_serial_num": str(controller_serial_num),
        "staff": str(staff),
        "departament":  str(departament),
        "controller": str(controller),
        "checkpoint": str(checkpoint),
        # "granted": 0
        # 'employee_photo': str(staff.employee_photo),
    }

    if accessible_gates != None:
        if checkpoint in accessible_gates:
            message.update({"granted": 1})
            data_monitor.update({"granted": 1})
    
    MonitorCheckAccess.objects.create(
        staff=staff, controller=controller, data_monitor=message
    )

    serializer_data_monitor = json.dumps(data_monitor)
    try:
        socket.websocket_receive(event=serializer_data_monitor)
    except:
        print(f'[=INFO=] Никто не подключен к сокетам')
    return message


def get_all_available_passes_for_employee(obj):
    return obj.access_profile.checkpoints.all()


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
        print(f'operation_type == "check_access" ------>>>>\n {message}___{meta}')
        granted = add_check_access_in_monitor_event(message=message, meta=meta)
        return granted
    elif operation_type == 'events':
        print(f'operation_type == "events" ------>>>>\n {message}___{meta}')
        add_events_in_monitor_event(message=message, meta=meta)
    else:
        pass


def add_check_access_in_monitor_event(message: dict, meta: dict) -> int:
    date_time_created = datetime.datetime.now()
    date_time_created = date_time_created.strftime("%Y-%m-%d %H:%M:%S")
    try:
        staff = Staffs.objects.get(pass_number=message['card'])
    except:
        staff = None
    try:
        controller = Controller.objects.get(serial_number=meta["serial_number"])
        checkpoint = controller.checkpoint
    except:
        controller = None
        checkpoint = None

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
    return granted


def add_events_in_monitor_event(message: dict, meta: dict):
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
        except:
            print(f'[=WARNING=] Event with unknown card number: {event["card"]}')
            staff = None
        try:
            objs_for_save_BD.append(
                MonitorEvents(
                    operation_type = operation_type,
                    time_created = event['time'],
                    card = event['card'],
                    staff = staff,
                    controller = controller,
                    checkpoint = checkpoint,
                    granted = None,
                    event = event['event'],
                    flag = event['flag'],
                    data_monitor_events = message
                )
            )
        except:
            pass
    MonitorEvents.objects.bulk_create(objs=objs_for_save_BD, batch_size=batch_size)


def give_issue_permission(staff = None, checkpoint = None):
    pass
    if staff == None or checkpoint == None:
        return 0
    try:
        accessible_gates = staff.access_profile.checkpoints.all()
    except:
        pass

    if checkpoint in accessible_gates:
        return 1

