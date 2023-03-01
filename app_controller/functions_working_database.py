import json

from app_controller.models import Controller, Event
from app_skud.models import Staffs, MonitorCheckAccess
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
        num_card = int(message["card"])
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
    else:
        message.update({"granted": 0})
        data_monitor.update({"granted": 0})
        MonitorCheckAccess.objects.create(
            staff=staff, controller=controller, data_monitor=message
        )


    serializer_data_monitor = json.dumps(data_monitor)
    try:
        socket.websocket_receive(event=serializer_data_monitor)
    except:
        print(f'[=INFO=] Никто не подключен к сокетам')

    return message
