import json
import datetime

from django.shortcuts import render

from django.http import JsonResponse

from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView

from django.views.decorators.csrf import csrf_exempt

from .models import Controller

from .handlers import (
    get_list_controller_messages,
    controller_message_handling
)

from .server_signals import (
    SET_ACTIVE, SET_MODE
)


@csrf_exempt
def controller_request_receiver_gateway(request):
    """Функция для представления стартовой страницы(логин),
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
    controller_message_list = get_list_controller_messages(body=body)
    processed_messages = controller_message_handling(data=controller_message_list)
    response = ResponseModel(message_reply=processed_messages)
    return JsonResponse(data=response, safe=False)


def ResponseModel(message_reply: list | dict) -> dict:
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
        "date": datetime.datetime.now(),
        "interval": 10,  # значение из примера, не знаю на что влияет
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
    success_url = "/"  # HARDCODE!!!!!!!                 
    fields = [  
        "controller_type",  
        "controller_activity",  
        "controller_online",  
        "controller_mode",  
        "checkpoint",  
    ]  

    
    def post(self, request, *args, **kwargs):  
        form = self.get_form()  
        send_data = dict(form.data)  
        set_active = SET_ACTIVE(send_data=send_data)  
        set_mode = SET_MODE(send_data=send_data)  
        resp = [set_active, set_mode]  
        resonse = ResponseModel(f=resp)  
        return JsonResponse(data=resonse, safe=False)  


class ControllerDeleteView(DeleteView):  
    model = Controller  
    template_name_suffix = "_delete_form"  
    success_url = "/"  # HARDCODE!!!!!!!                 
