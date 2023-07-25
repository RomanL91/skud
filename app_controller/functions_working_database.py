import json, pytz
import channels.layers

from django.db.models import Q

from asgiref.sync import async_to_sync

from datetime import datetime, date, timedelta

from core.settings import MEDIA_URL
 
from app_controller.models import (
    Controller
)
from app_controller.views import (
    ResponseModel
)
from app_controller.server_signals import (
    send_GET_request_for_controllers
)

from app_skud.utilities import convert_hex_to_dec_and_get_employee

from app_skud.models import (
    Staffs,  
    MonitorEvents)

from app_skud.utils_to_microscope import (
    get_archiveevents_from_microscope, login, passw,
    URL_SDK, ARCHIVEEVENTS)


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
    reader = message['reader']
    all_staff = Staffs.objects.all()
    tz = pytz.timezone('Etc/GMT-6') # это в конфиг файл
    date_time_created = datetime.now(tz=tz)
    
    start_t = date_time_created - timedelta(hours=6, seconds=10)
    end_t = date_time_created - timedelta(hours=6)
    start_t = start_t.strftime("%d.%m.%Y+%H:%M:%S")
    end_t = end_t.strftime("%d.%m.%Y+%H:%M:%S")

    date_time_created = date_time_created.strftime("%Y-%m-%d %H:%M:%S")

    try:
        staff = convert_hex_to_dec_and_get_employee(employee_pass=message['card'], all_staff=all_staff)
        try:
            photo = staff.employee_photo.url
        except Exception as e:
            photo = None
            print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')
        staff_last_name = staff.last_name 
        staff_first_name = staff.first_name
        staff_patronymic = staff.patronymic
        departament = staff.department.name_departament if staff.department is not None else ' --- '
    except Exception as e:
        print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')
        staff = photo = staff_last_name = staff_first_name = departament = staff_patronymic = None
        staff_last_name = staff_first_name = departament = staff_patronymic = ' --- '
    try:
        controller = Controller.objects.get(serial_number=meta["serial_number"])
        checkpoint = controller.checkpoint
        id_chekpoint = checkpoint.pk
        serial_number = controller.serial_number
    except Exception as e:
        controller = checkpoint = serial_number, id_chekpoint = None
        print(f'[=EXCEPTION=] f:add_check_access_in_monitor_event -> {e}')

    granted = give_issue_permission(staff=staff, checkpoint=checkpoint, reader=reader, start=start_t, end=end_t)
    late_status = get_late_status____(staff=staff, reader=reader, type_operations=message['operation'])
    print(f'late_status ----------->>>>>>>>>> {late_status}')
    if message['card'] == 'OpenButtonPressed':
        granted = 1
        message['card'] = 'Open Button'
    ddd = {
        'dep': departament, 'photo': photo, 'message': message,
        "last_name": staff_first_name, "first_name":  staff_last_name, "patronymic": staff_patronymic,
        'granted': granted,
        'direct': 'Вход' if reader == 1 else 'Выход',
        'late_status': late_status
    }

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
        data_monitor_events = ddd
    )
    obj_for_BD.save()

    # ==============================================================
    event = 'Доступ запрешен'
    if granted:
        event = 'Доступ разрешен'
    if message['card'] == 'Open Button':
        event = 'Open Button'
    data = {
            "event_initiator": {
                "last_name": staff_last_name,
                "first_name": staff_first_name,
                "patronymic": staff_patronymic,
                "department": {"name_departament": departament},
                "employee_photo": photo
            },
            "controller": {"checkpoint": {"description_checkpoint": str(checkpoint)}, "id": str(id_chekpoint)},
            "time": date_time_created,
            "flag": ddd['direct'],
            "data_event": {"event": event},
            'late_status': late_status
        }
    try:
        channels_ = channels.layers.get_channel_layer()
        async_to_sync(channels_.group_send)("client", {"type": "receive", "text_data": data})
    except Exception as e:
        print(f'[=INFO=] Page with WebSocket not running!')
        print(f'[=ERROR=] {e}')
    # ==============================================================
    return granted


def give_granted(event_num: int) -> int:
    granted_0 = [2, 4, 6, 7, 14, 17, 26, 28, 30]
    if event_num in granted_0:
        return 0
    else:
        return 1
    

def get_information_about_employee_to_send(st) -> dict[None | str]:
    if st != None:
        return {
            'photo': str(st.employee_photo),
            'staff_last_name': st.last_name,
            'staff_first_name': st.first_name,
            'patronymic': st.patronymic,
            'departament': str(st.department)
        }
    else:
        return {
            'photo': None,
            'staff_last_name': ' --- ',
            'staff_first_name': ' --- ',
            'patronymic': ' --- ',
            'departament': ' --- '
        }


def add_events_in_monitor_event(message: dict, meta: dict):
    # функция требует оптимизации
    # сохранение пакета с 10000 моделями занимает около 8 сек
    # стабильность есть, интерфейс отзывчив во время сохранения
    # задача на интерес оптимизации
    # ранее был результат 1,5 сек в худщем случае!
    all_staff = Staffs.objects.all()
    try:
        operation_type = message['operation']
    except:
        pass
    try:
        controller = Controller.objects.get(serial_number=meta["serial_number"])
        checkpoint = controller.checkpoint
        id_checkpoint = checkpoint.pk
    except:
        print(
            f'[=WARNING=] The server receives a signal EVENTS from an unknown controller: {meta["serial_number"]}'
        )
        id_checkpoint = None
        controller = None
        checkpoint = None
    try:
        list_events = message["events"]
        format_str = "%Y-%m-%d %H:%M:%S"
        for el in list_events:
            date_time_format = datetime.strptime(el["time"], format_str)
            date_time = date_time_format.strftime(format_str)
            el["time"] = date_time
    except Exception as e:
        print(f"[=ERROR=] Failed to get list of events!")
        print(f"[=ERROR=] The {e}!")

    print(f'list_events ---->>> {list_events}')

    for i in list_events:
        try:
            staff = convert_hex_to_dec_and_get_employee(employee_pass=i['card'], all_staff=all_staff)
            staff_last_name = staff.last_name
            staff_first_name = staff.first_name
            staff_patronymic = staff.patronymic
            departament = staff.department.name_departament
            try:
                photo = staff.employee_photo.url
            except Exception as e:
                print(f'[=EXCEPTION=] f:add_events_in_monitor_event -> {e}')
                photo = None
        except Exception as e:
            print(f'[=EXCEPTION=] f:add_events_in_monitor_event -> {e}')
            staff = photo = staff_last_name = staff_first_name = departament = staff_patronymic = None
            staff_last_name = staff_first_name = departament = staff_patronymic = ' --- '

        if i == 'OpenButtonPressed':
            departament = photo = staff_first_name = staff_last_name = staff_patronymic = ' --- '

        reader = i['direct']
        print(f'reader ----------->>>>>>>>>> {reader}')
        late_status = get_late_status____(staff=staff, reader=reader, type_operations=operation_type, time_event=i['time'])
        print(f'late_status ----------->>>>>>>>>> {late_status}')


        ddata = {
                'dep': departament, 'photo': photo,
                "last_name": staff_first_name, "first_name":  staff_last_name, "patronymic": staff_patronymic,
                'granted': give_granted(event_num=i['event']),
                'direct': 'Вход' if i['direct'] == 1 else 'Выход', 'late_status': late_status
            }
        i.update(ddata)

    obj_to_save_and_send = [
        MonitorEvents(
            operation_type = operation_type,
            time_created = v['time'],
            card = v['card'] if v['card'] != 'OpenButtonPressed' else 'Open Button',
            staff = str(convert_hex_to_dec_and_get_employee(employee_pass=v["card"], all_staff=all_staff)),
            # staff = f'{staff_last_name} {staff_first_name} {staff_patronymic}',
            controller = controller,
            checkpoint = checkpoint,
            granted = give_granted(event_num=v['event']),
            event = v['event'],
            flag = v['flag'],
            data_monitor_events = v
        ) for v in list_events
    ]
    
    channels_ = channels.layers.get_channel_layer()
    for i in obj_to_save_and_send:
        staff = convert_hex_to_dec_and_get_employee(employee_pass=i.card, all_staff=all_staff)
        data = get_information_about_employee_to_send(st=staff)
        event = 'Доступ запрешен'
        if i.granted:
            event = 'Доступ разрешен'
        data = {
            "event_initiator": {
                "last_name": data['staff_last_name'],
                "first_name": data['staff_first_name'],
                "patronymic": data['patronymic'],
                "department": {"name_departament": data['departament']},
                "employee_photo": f"/{MEDIA_URL}{data['photo']}"
            },
            "controller": {"checkpoint": {"description_checkpoint": str(checkpoint)}, "id": str(id_checkpoint)},
            "time": i.time_created,
            "flag": i.data_monitor_events['direct'],
            "data_event": {"event": event if i.card != 'Open Button' else i.card},
            'late_status': late_status
        }

        today = str(date.today())
        event_day, event_hour = i.time_created.split(' ')

        if today == event_day:
            try:
                async_to_sync(channels_.group_send)("client", {"type": "receive", "text_data": data})
            except Exception as e:
                print(f'[=INFO=] Page with WebSocket not running!')
                print(f'[=ERROR=] {e}')

    MonitorEvents.objects.bulk_create(objs=obj_to_save_and_send)


def give_issue_permission(staff = None, checkpoint = None, reader = None, start = None, end = None):
    if staff == None or checkpoint == None:
        return 0
    try:
        if reader != 1:
            reader = 'ВЫХОД'
        else:
            reader = 'ВХОД'
        cameras = checkpoint.camera_set.get(checkpoint=checkpoint, direction=reader)
        id_camera_microscope = cameras.id_camera_microscope
        list_external_id_from_microscope = get_archiveevents_from_microscope(
            url_api_sdk=URL_SDK, point=ARCHIVEEVENTS, login=login, passw=passw,
            time_start=start, time_end=end, id_cam_microscope=id_camera_microscope
        )
    except Exception as e:
        print(f'---------e---------->>> {e}')
        list_external_id_from_microscope = []
        return 0

    try:
        accessible_gates = staff.access_profile.checkpoints.all()
    except Exception as e:
        return 0

    if checkpoint in accessible_gates and str(staff.pk) in list_external_id_from_microscope:
        return 1
    return 0


def get_events_for_range_dates(start_date: tuple, end_date: tuple):
    start_date = date(*start_date)
    end_date = date(*end_date)
    obj_BD_date_filter = MonitorEvents.objects.filter(
        time_created__range=(start_date, end_date)
    )
    return obj_BD_date_filter


def get_late_status____(staff, reader, type_operations=None, time_event=None):
    try:
        tz = pytz.timezone('Etc/GMT-6') # это в конфиг файл
        time_now = datetime.now(tz=tz).replace(tzinfo=None)
        week_day = time_now.strftime('%A').lower()
        if staff == None:
            return f'Не известный сотрудник'
        staff_time_profile = staff.time_profale
        if staff_time_profile == None:
            return f'Без профиля доступа по времени'
        else:
            mask_staff_time_profile = staff_time_profile.time_profile_data
            begin_day, end_day  = mask_staff_time_profile[week_day]
            datetime_obj_begin_day = datetime.strptime(begin_day, '%H:%M:%S').time()
            datetime_obj_end_day = datetime.strptime(end_day, '%H:%M:%S').time()
            try:
                events_staff_today = MonitorEvents.objects.filter(
                    Q(staff=staff), Q(time_created__date=time_now.date())
                )
                print(f'event_staff_today ---->>>> {events_staff_today}')
            except:
                print(f'не получилось отфильтровать событие')
            time_now = time_now.time()
            t_end_day = datetime.strptime(f'{end_day}', '%H:%M:%S')
            t_begin_day = datetime.strptime(f'{begin_day}', '%H:%M:%S')
            t_time_now = datetime.strptime(f'{time_now}', '%H:%M:%S.%f')

            if type_operations == 'events':
                time_event = time_event.split(' ')[1] + '.0'
                t_time_now = datetime.strptime(time_event, '%H:%M:%S.%f')
                time_now = t_time_now.time()
            
            if events_staff_today.count() != 0:
                previous_event = events_staff_today[events_staff_today.count() - 1]
                derict_previous_event = previous_event.data_monitor_events['direct']
                if datetime_obj_begin_day < time_now < datetime_obj_end_day:
                    if reader == 1 and derict_previous_event == 'Выход':
                        return f'повторный вход'
                    elif reader == 1 and derict_previous_event == 'Вход':
                        return f'не известно время выхода'
                    elif reader == 2 and derict_previous_event == 'Выход':
                        return f'не известно время входа'
                    elif reader == 2 and derict_previous_event == 'Вход':
                        return f'до конца рабочего дня {t_end_day - t_time_now}'
                elif datetime_obj_begin_day > time_now:
                    if reader == 1 and derict_previous_event == 'Выход':
                        return f'до начала рабочего дня {t_begin_day - t_time_now}'
                    elif reader == 1 and derict_previous_event == 'Вход':
                        return f'не известно время выхода'
                    elif reader != 1 and derict_previous_event == 'Выход':
                        return f'не известно время входа'
                    elif reader != 1 and derict_previous_event == 'Вход':
                        return f'до начала рабочего дня {t_begin_day - t_time_now}'
                elif datetime_obj_end_day < time_now:
                    if reader == 1 and derict_previous_event == 'Выход':
                        return f'вход вне графика'
                    elif reader == 1 and derict_previous_event == 'Вход':
                        return f'не известного времени выхода'
                    elif reader != 1 and derict_previous_event == 'Выход':
                        return f'не известно время входа'
                    elif reader != 1 and derict_previous_event == 'Вход':
                        return f'вы были на работе {t_time_now - t_begin_day}'
            else:
                if datetime_obj_begin_day < time_now < datetime_obj_end_day:
                    if reader == 1:
                        return f'опоздание на {t_time_now - t_begin_day}'
                    else:
                        return f'не известно время входа'
                elif datetime_obj_end_day > time_now and reader == 1:
                    return f'до начала рабочего дня {t_begin_day - t_time_now}'
                elif datetime_obj_end_day > time_now and reader != 1:
                    return f'не известно время входа'
                elif datetime_obj_begin_day < time_now and reader == 1:
                    return f'до начала рабочего дня {t_begin_day - t_time_now}'
                elif datetime_obj_begin_day < time_now and reader != 1:
                    return f'не известно время входа'
    except Exception as e:
        print(f'-----e------>>>> {e}')
        return f'не удалось обработать статус времени события'


def get_events_by_days(qs):
    data = {}
    for el in qs:
        subdata = {}
        subdata.setdefault(el.time_created, el)
        if el.staff not in data:
            data.setdefault(el.staff, [subdata,])
        else:
            data[el.staff].append(subdata)

    return data
