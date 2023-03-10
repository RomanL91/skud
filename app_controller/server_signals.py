# блок сигналов
# сигналы сервера на контроллер
# ===============================================================================
# данные функции нужно дописать, так как большинство из ни требует введение
# параметров, где то параметры должны присваиваться автоматически.
# Так же нужна будет функция генерирования  ID, но это не точно.
# Стоит не забыть то, что результаты данных функций нужно отправлять через
# ResponseModel, которая добавлят шапку(дата, интервал, сообщения)
import requests, aiohttp



URL = 'http://192.168.0.341:8080'


async def async_send_GET_request_for_controllers(url: str, data = None):
    print(f'[=INFO=] I"m trying to send this: {data} to: {url}')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, data=data, ssl=False) as response:
                status_code = await response.status
                print(f'status_code --->>> {status_code}')
        except Exception as e:
            print(f"[=ERROR=] Sending failed! \n[=ERROR=]: {e}")


def send_GET_request_for_controllers(url: str, data = None):
    print(f'[=INFO=] I"m trying to send this: {data} to: {url}')
    try:
        response_for_controllers = requests.get(url=url, data=data)
        print(f'response_for_controllers --->>> {response_for_controllers}')
    except Exception as e:
        print(f"[=ERROR=] Sending failed! \n[=ERROR=]: {e}")


def SET_ACTIVE(send_data: dict):
    try:
        active = int(send_data["controller_activity"][-1])
        online = int(send_data["controller_online"][-1])
    except:
        pass  # HARDCODE !!!!

    signal_for_controller = {
        "id": 123456789,  # HARDCODE !!!!
        "operation": "set_active",
        "active": active,
        "online": online,
    }
    return signal_for_controller


def SET_MODE(send_data: dict):
    try:
        mode = int(send_data["controller_mode"][-1])
    except:
        pass  # HARDCODE !!!!

    signal_for_controller = {
        "id": 123456789,  # HARDCODE !!!!
        "operation": "set_mode",
        "mode": mode,
    }
    return signal_for_controller


def OPEN_DOOR():
    signal_for_controller = {"id": 123456789, "operation": "open_door", "direction": 0}
    # direction - 0 - вход, 1 – выход.
    # Ответ:
    # {
    # "id":123456789,
    # "success ":1
    # }


def SET_TIMEZONE():
    signal_for_controller = {
        "id": 123456789,
        "operation": "set_timezone",
        "zone": 0,
        "begin": "00:00",
        "end": "23:59",
        "days": "11111110",
    }
    # !!! функционал в SET_ACTIVE !!!


def SET_DOOR_PARAMS():
    signal_for_controller = {
        "id": 123456789,
        "operation": "set_door_params",
        "open": 30,
        "open_control": 50,
        "close_control": 50,
    }
    # open - время подачи сигнала открывания замка (в 1/10 секунды).
    # open_control - время контроля открытия двери (в 1/10 секунды).
    # close_control - время контроля закрытия двери (в 1/10 секунды).
    # Ответ:
    # {
    # "id":123456789,
    # "success ":1
    # }


def ADD_CARD(card_number):
    signal_for_controller = {
        "id": 123456789,
        "operation": "add_cards",
        "cards": [
            {"card": str(card_number), "flags": 0, "tz": 255},
        ],
    }
    return signal_for_controller


def DEL_CARDS(card_number):
    signal_for_controller = {
        "id": 123456789,
        "operation": "del_cards",
        "cards": [{"card": card_number},],
    }
    return signal_for_controller


def CLEAR_CARDS():
    signal_for_controller = {
        "id": 123456789,
        "operation": "clear_cards",
    }
    # Ответ:
    # {
    # "id":123456789,
    # "success ":1
    # }


# ===============================================================================