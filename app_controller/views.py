import json
import datetime

from django.shortcuts import redirect

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from .server_signals import (
    URL,
    send_GET_request_for_controllers,
    # async_send_GET_request_for_controllers # асинхронный вариант 
)


@csrf_exempt
def controller_request_receiver_gateway(request):
    """
    Функция для представления стартовой страницы(логин),
    а также для прима POST запросов от контроллеров.

    Args:
        request (<class 'django.core.handlers.asgi.ASGIRequest'>):
        запрос клиентской стороны.

    Returns:
        HTML: при GET запросе.

        JsonResponse: возращает при POST запросе от
        контроллера.
    """
    if request.method == "GET":
        return redirect(to='/admin/')   #HARDCODE
    body_unicode = request.body.decode("utf-8")
    try:
        body = json.loads(body_unicode)
    except Exception as e:
        response = {"error": f"huev json, dust do it: {e}"}
        return JsonResponse(data=response, safe=False)
    try:
        serial_num_controller = body['sn']
    except:
        print(f"[==ERROR==] Controller serial number unknown!")

    controller_message_list = get_list_controller_messages(body=body)
    processed_messages = controller_message_handling(data=controller_message_list)
    response = ResponseModel(message_reply=processed_messages, serial_number_controller=serial_num_controller)
    response_serializer = json.dumps(response)
    send_GET_request_for_controllers(url=URL, data=response_serializer) # синхроный вариант
    # asyncio.run(
        # async_send_GET_request_for_controllers(url=URL, data=response_serializer)
    # ) 
    return JsonResponse(data=response, safe=False)


def ResponseModel(message_reply: list | dict, serial_number_controller: int = None) -> dict:
    """
    Функция для типизации ответа.
    Args:
        message_reply (list | dict): принимает готовое
        сообщение или список таких сообщений, которые
        будут отправлены контроллеру.

    Returns:
        dict: объект Python для последущей трансформации
        в JSON.
    """
    data_resonse = {
        "date": str(datetime.datetime.now()),
        "interval": 10,  # значение из примера, не знаю на что влияет
        "sn": serial_number_controller,
        "messages": "",
    }
    if isinstance(message_reply, list):
        data_resonse["messages"] = message_reply
    else:
        data_resonse["messages"] = [
            message_reply,
        ]
    return data_resonse


# ===============================================================================
# цикличный импорт
from .handlers import (
    get_list_controller_messages,
    controller_message_handling
)
