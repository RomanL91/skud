# блок сигналов
# сигналы сервера на контроллер
# ===============================================================================
# данные функции нужно дописать, так как большинство из ни требует введение
# параметров, где то параметры должны присваиваться автоматически.
# Так же нужна будет функция генерирования  ID, но это не точно.
# Стоит не забыть то, что результаты данных функций нужно отправлять через
# ResponseModel, которая добавлят шапку(дата, интервал, сообщения)




def SET_ACTIVE(send_data: dict):
    # print(f"send_data -->> {send_data}")
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
    # print(f"send_data -->> {send_data}")
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


def ADD_CARDS():
    signal_for_controller = {
        "id": 123456789,
        "operation": "add_cards",
        "cards": [
            {"card": "00B5009EC1A8", "flags": 0, "tz": 255},
            {"card": "0000000FE32A2", "flags": 32, "tz": 255},
        ],
    }
    # cards - массив карт для добавления.
    # card - номер карты в шестнадцатеричном виде (см. ПРИЛОЖЕНИЕ 2).
    # flags - флаги для карты (8 - блокирующая карта, 32 - короткий код карты (три байта)).
    # tz - временные зоны для карты.
    # Ответ:
    # {
    # "id":123456789,
    # "success ":1
    # }


def DEL_CARDS():
    signal_for_controller = {
        "id": 123456789,
        "operation": "del_cards",
        "cards": [{"card": "000000A2BA93"}, {"card": "000000A2A18A"}],
    }

    # cards - массив карт для удаления, содержит номера карты в шестнадцатеричном виде (см.
    # ПРИЛОЖЕНИЕ 2).
    # Ответ:
    # {
    # "id":123456789,
    # "success ":1
    # }


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