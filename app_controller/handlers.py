from app_controller.functions_working_database import (
    add_events_database,
    add_controller_database,
    add_access_check_database_and_issue_permission,
)

from app_controller.controller_signals import (
    CHECK_ACCESS,
    PING,
    EVENTS,
    reply_confirmation,
)

# ========================================================================
# '''
# На данный момент данные три функции для обработки сигналов от
# контролерров стоит рассатривать как единый конвеер.
# Обработчик 1 уровня -->> обработчик 2 уровня -->> обработчик 3 уровня.
# Каждому уровню дана своя определенная задача.
# '''
# ========================================================================


def message_handler(message: dict, meta: dict = None):
    """Функция обработчик 3 уровня.
        Функция обрабатывает каждое конкретное сообщение.
        Считывает тип сигнала из сообщения.
        Запускает ту или иную логику исходя из типа сигнала.

    Args:
        message (dict): сообщение контроллера.
        meta (dict, optional): Инфо о контроллере. Defaults to None.

    Returns:
        в зависимости от типа сигнала полученного сообщения.
    """
    if "success" in message.keys():
        message["operation"] = "reply"
    list_message_types = ["power_on", "check_access", "ping", "events", "reply"]
    try:
        message_id = message["id"]
        message_operation_type = message["operation"]
    except KeyError as e:
        print(f"[=ERROR=] The {e} key does not exist. Error getting key!")
        return e

    if message_operation_type not in list_message_types:
        print(
            f"[==ERROR==] Received an unknown operation type from the controller. Message id: {message_id}"
        )
    else:
        match message_operation_type:
            case "power_on":
                print("[=INFO=] The controller sent a POWER_ON signal")
                add_controller_database(message=message, meta=meta)
            case "check_access":
                print("[=INFO=] The controller sent a CHECK_ACCESS signal")
                message = add_access_check_database_and_issue_permission(
                    message=message, meta=meta
                )
                # print(f"msg_check_access -->>>> {message}")
                # if message['granted']:
                #     print(f'---->>> OPEN DOOR <<<----')
                return CHECK_ACCESS(message=message)
            case "ping":
                print("[=INFO=] The controller sent a PING signal")
                return PING(message=message)
            case "events":
                print("[=INFO=] The controller sent a EVENTS signal")
                add_events_database(message=message, meta=meta)
                return EVENTS(message=message)
            case "reply":
                print("[=INFO=] The controller sent a CONFIRMATION SIGNAL signal")
                return reply_confirmation(message=message)


def controller_message_handling(data: dict) -> list | dict:
    """Функция обработчик 2 уровня.
        Выполняется после функции обработчика 1 уровня.
        Основное назначение: в зависимости от занчения переменной
        flag (установленной на 1 уровне) выполнить запуск
        обработчика 3 уровня один или несколько раз.

    Args:
        data (dict): только результат функции обработчика
        1 уровня.

    Returns:
        (list | dict): множественные | единичные ответы.
    """
    try:
        flag = data["flag"]
        messages = data["messages"]
        meta = data["meta"]
    except KeyError as e:
        print(f"[=ERROR=] The {e} key does not exist. Error getting key!")
        return {"KeyError": e.__str__()}

    if flag == "single":
        message = messages[-1]
        try:
            return message_handler(message=message, meta=meta)
        except KeyError as e:
            print(f"[=ERROR=] The {e} key does not exist. Error getting key!")
            return e
    elif flag == "many":
        response_list_for_controller = []
        for msg in messages:
            f = message_handler(message=msg, meta=meta)
            response_list_for_controller.append(f)
        return response_list_for_controller


def get_list_controller_messages(body: dict) -> dict:
    """Функция обработчик 1 уровня.
        Функция получения списка сообщений.
        Основная логика - добавление флагов
        "flag": "single" - если от контроллера поступило
        только одно сообщение,
        "flag": "many" - если от контроллера поступило
        несколько сообщений в одном сигнале.

    Args:
        body (dict): тело POST запроса от контроллера.

    Returns:
        dict: Сообщение с добавленным флагом или же
        объект dcit Python с ключом request.
    """
    if isinstance(body, dict):
        print(f"[=INFO=] Correct type: {type(body)}.")
        if len(body) > 0:
            try:
                type_controller: str = body["type"]
                serial_number: int = body["sn"]
                messages: list = body["messages"]
                meta: dict = {"type": body["type"], "serial_number": serial_number}
                if len(messages) == 0:
                    print(
                        f"[=ERROR=] Controller: type: {type_controller}, serial number: {serial_number} returned an empty list of messages."
                    )
                    return {
                        "request": f"[=ERROR=] Controller: type: {type_controller}, serial number: {serial_number} returned an empty list of messages."
                    }  # возможно нужно raise а не return.......
                elif len(messages) == 1:
                    print(
                        f"[=INFO=] Controller: type: {type_controller}, serial number: {serial_number} returned single message."
                    )
                    return {"flag": "single", "messages": messages, "meta": meta}
                else:
                    print(
                        f"[=INFO=] Controller: type: {type_controller}, serial number: {serial_number} returned many messages."
                    )
                    return {"flag": "many", "messages": messages, "meta": meta}
            except KeyError as e:
                print(f"[=ERROR=] The {e} key does not exist. Error getting key!")
                return e
        else:
            print(f"[=ERROR=] Empty request.")
    else:
        print(f"Incorrect data type: {type(body)}.")
