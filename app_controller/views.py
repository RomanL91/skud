import json, pytz, asyncio

from datetime import datetime

from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .server_signals import (
    send_GET_request_for_controllers,
    async_send_GET_request_for_controllers,
    DEL_CARDS, ADD_CARD
)
from .forms import AddNumberCardsInControllerForm
from app_controller.models import Controller


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
        print(f'[=INFO=] Body request: {body}')
    except Exception as e:
        response = {"error": f"huev json, dust do it: {e}"}
        return JsonResponse(data=response, safe=False)
    try:
        serial_num_controller = body['sn']
    except:
        print(f"[==ERROR==] Post request without controller serial number!")
    controller_message_list = get_list_controller_messages(body=body)
    processed_messages = controller_message_handling(data=controller_message_list)
    response = ResponseModel(message_reply=processed_messages, serial_number_controller=serial_num_controller)
    # response_serializer = json.dumps(response)
    # try:
    #     controller_from_BD = Controller.objects.get(serial_number = serial_num_controller)
    #     url_for_answer = controller_from_BD.other_data["controller_ip"]
    # except Exception as e:
    #     url_for_answer = None
    #     print(f"[==ERROR==] {e}!!!")
    # # TO DO закоментировать
    # send_GET_request_for_controllers(url=url_for_answer, data=response_serializer) # синхроный вариант
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
    tz = pytz.timezone('Etc/GMT-6') # это в конфиг файл
    date_time_created = datetime.now(tz=tz)
    date_time_created = date_time_created.strftime("%Y-%m-%d %H:%M:%S")

    data_resonse = {
        "date": date_time_created,
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


def del_card_from_controller(request, cards_number, serial_number):
    url_controller = Controller.objects.get(serial_number=serial_number).other_data['controller_ip']
    signal_del_cards_for_controller = DEL_CARDS(card_number=cards_number)
    request_for_controller = ResponseModel(message_reply=signal_del_cards_for_controller, serial_number_controller=int(serial_number))
    request_for_controller = json.dumps(request_for_controller)
    send_GET_request_for_controllers(url=url_controller, data=request_for_controller)
    return redirect(to=request.META["HTTP_REFERER"])


def add_card(request, serial_number):
    url_controller = Controller.objects.get(serial_number=serial_number).other_data['controller_ip']
    form = AddNumberCardsInControllerForm(request.POST)
    if request.method == 'POST':
        card_number = form.data['card_number']
        signal_add_cards_for_controller = ADD_CARD(card_number=card_number)
        request_for_controller = ResponseModel(message_reply=signal_add_cards_for_controller, serial_number_controller=int(serial_number))
        request_for_controller = json.dumps(request_for_controller)
        send_GET_request_for_controllers(url=url_controller, data=request_for_controller)
        # asyncio.run(
            # async_send_GET_request_for_controllers(url=url_controller, data=request_for_controller)
        # )
        return redirect(to=request.META["HTTP_REFERER"])
    return render(request, 'app_controller/admin/form_adding_card_in_controller.html', context={'form': form})


# ===============================================================================
# цикличный импорт
from .handlers import (
    get_list_controller_messages,
    controller_message_handling
)
