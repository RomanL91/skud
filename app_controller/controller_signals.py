# блок сигналов
# сигналы от контроллера
# частично ХАРДХОРНЫЕ ответы, исправим
# 
# 
# ===============================================================================

def CHECK_ACCESS(message: dict):
    # согласно документации посылается контроллером только в режиме ONLINE
    try:
        granted = message["granted"]
    except:
        granted = 0
    data_resonse = {
        "id": message["id"],  # вставляю ID из сообщения, но не факт что правильно
        "operation": "check_access",
        "granted": granted,  # granted - 1 - проход разрешен, 0 – запрещен.
    }

    return data_resonse


def PING(message: dict):
    # ответ на этот сигнал описан на странице 4 (сообщения для контроллера??)
    data_resonse = {"messages": []}
    return data_resonse


def EVENTS(message: dict):
    list_events = message["events"]
    data_resonse = {
        "id": message["id"],  # вставляю ID из сообщения, но не факт что правильно
        "operation": "events",
        "events_success": len(list_events),
    }
    return data_resonse


def reply_confirmation(message: dict):
    # вообще логика этой функции: она для того, чтобы понять, что контроллер
    # одобрил или не одобрил запрос к нему под конкретным ID
    # то есть я могу получить от контроллера месседж, что к примеру мой запрос SET_ACTIVE
    # не прошел(или что там еще) и контроллер вернул мне 0 – ошибка
    # значит я должен взять эту операцию по ID и поробовать например ее повторить
    # или/и рассказать оператору об этом.
    #
    data_reply_confirmation = {
        "NOTEBANE": "ЭТО ДЛЯ ТЕСТА, ПРОВЕРКА, МОГУ Я ПАРСИТЬ ЭТОТ ОТВЕТ КОНТРОЛЛЕРА",
        "NOTEBANE_1": "это подверждающий ответ контроллера, если 1 - все ок, если 0 - запуск еще чего...",
        "id": message["id"],
        "success": 1,  # success - 1- команда принята, 0 – ошибка. Сюда должно подставляться решение контроллера
    }
    return data_reply_confirmation


# ===============================================================================