import json
import datetime
import requests

from django.shortcuts import render, redirect

from django.http import JsonResponse

from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView

from django.views.decorators.csrf import csrf_exempt

from .models import Controller

from .server_signals import (
    URL,
    SET_ACTIVE, SET_MODE,
    send_GET_request_for_controllers
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
        return render(request, "app_controller/root.html")
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
    send_GET_request_for_controllers(url=URL, data=response_serializer)
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
# classViews контроллеров                               
class ControllersListView(ListView):  
    model = Controller  
    context_object_name = "controllers" 


class ControllerDetailView(DetailView):  
    model = Controller  
    context_object_name = "controller"  


class ControllerUpdateView(UpdateView):  
    model = Controller  
    template_name_suffix = "_update_form"  
    # success_url = "/"  # HARDCODE!!!!!!!                 
    fields = [  
        "controller_type",  
        "controller_activity",  
        "controller_online",  
        "controller_mode",  
        "checkpoint",  
    ]  

    
    def post(self, request, *args, **kwargs):  
        form = self.get_form()  
        serial_num_controller = self.get_object().serial_number
        send_data = dict(form.data)  
        print(f'send_data --->>> {send_data}')
        set_active = SET_ACTIVE(send_data=send_data)  
        set_mode = SET_MODE(send_data=send_data)  
        resp = [set_active, set_mode]  
        resonse = ResponseModel(message_reply=resp, serial_number_controller=serial_num_controller)  
        ddd = json.dumps(resonse)
        try:
            r = requests.get('http://192.168.0.34:8080', data=ddd)
            print(f'r------>>> {r}')
        except Exception as e:
            print(f"[=ERROR=] Sending failed! \nError: {e}")
        return redirect(to=request.META['HTTP_REFERER'])
        
        return JsonResponse(data=resonse, safe=False)  


class ControllerDeleteView(DeleteView):  
    model = Controller  
    template_name_suffix = "_delete_form"  
    success_url = "/"  # HARDCODE!!!!!!!                 


# ===============================================================================
# цикличный импорт
from .handlers import (
    get_list_controller_messages,
    controller_message_handling
)
