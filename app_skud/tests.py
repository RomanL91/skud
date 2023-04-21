from django.test import TestCase
import re
# Create your tests here.

n_1 = '0007339662' # "^([0-9]{10})$"
n_2 = '111.65166' # "^([0-9]{3}).([0-9]{5})$"
n_3 = '111,65166'
n_4 = '111,651661'
n_5 = '111/65166'
n_6 = '111651644'


def validation_and_formatting_of_pass_number(input_pass_num: str) -> dict:
    mask = ['000000']
    match input_pass_num:
        case num if len(num) == 10:
            try:
                pass_number = re.match("^([0-9]{10})$", num).group(0)
                hex_n = hex(int(pass_number))[2:]
                mask.append(hex_n)
                hex_pass_number = ''.join(mask).upper()
                return hex_pass_number
            except:
                pass_number = None
                return f'не корректный номер пропуска: {num}'

        case num if len(num) == 9:
            try:
                pass_number = re.match("^([0-9]{3})([\D])([0-9]{5})$", num)
                part_1_pass_number = pass_number.group(1)
                part_3_pass_number = pass_number.group(3)
                hex_s = hex(int(part_1_pass_number))[2:]
                mask.append(hex_s)
                hex_n = hex(int(part_3_pass_number))[2:]
                mask.append(hex_n)
                hex_pass_number = ''.join(mask).upper()
                return hex_pass_number
            except:
                pass_number = None
                return f'не корректный номер пропуска: {num}'

        case _:
            print('проверка не пройдена')


import json
from django.shortcuts import render, redirect

from app_controller.views import ResponseModel
from app_skud.models import *
from app_controller.models import *
from app_controller.server_signals import (
    ADD_CARD,
    DEL_CARDS,
    send_GET_request_for_controllers, 
    async_send_GET_request_for_controllers)


def get_list_controllers(list_checkpoints):
    print(f'get_list_controllers')
    list_controllers = []
    for checkpoint in list_checkpoints:
        controller = list(Controller.objects.filter(checkpoint=checkpoint))
        list_controllers.extend(controller)
    print(f'list_controllers --->>> {list_controllers}')
    return list_controllers


def give_signal_to_controllers(list_controllers, signal):
    for el in list_controllers:
        send_GET_request_for_controllers(
            url=el.other_data['controller_ip'],
            data=json.dumps(
                ResponseModel(
                    message_reply=signal,
                    serial_number_controller=el.serial_number
                )
            )
        )


def f(
    pass_number_obj_from_BD,
    list_checkpoints_obj_from_BD,
    request_access_profile,
    request_pass_number,
    change_access_profile,
    change_pass_number
): 
    try:
        old_pass_number = validation_and_formatting_of_pass_number(pass_number_obj_from_BD)
        print(f'old_pass_number --->>> {old_pass_number}')
    except:
        old_pass_number = None
        print(f'old_pass_number --->>> {old_pass_number}')
        pass

    try:
        new_pass_number = validation_and_formatting_of_pass_number(request_pass_number)
        print(f'new_pass_number --->>> {new_pass_number}')
        if len(new_pass_number) > 12:
            return f'Запись карты {request_pass_number}({new_pass_number}) на контроллеры НЕ произведена', 1
    except:
        print(f'new_pass_number --->>> {new_pass_number}')
        pass

    if change_access_profile == False and change_pass_number == True:
        list_controllers = get_list_controllers(list_checkpoints=list_checkpoints_obj_from_BD)
        signal_del_card = DEL_CARDS(card_number=old_pass_number)
        signal_add_card = ADD_CARD(card_number=new_pass_number)
        give_signal_to_controllers(list_controllers=list_controllers, signal=signal_del_card)
        give_signal_to_controllers(list_controllers=list_controllers, signal=signal_add_card)
        return (f'Удаляю старый пропуск {pass_number_obj_from_BD}({old_pass_number}) из контроллеров: {list_controllers}',
            f'Записываю карту {request_pass_number}({new_pass_number}) на контроллеры: {list_controllers}.', 0)

    if change_access_profile == True and change_pass_number == False:
        new_access_profile = AccessProfile.objects.get(pk=request_access_profile)
        list_checkpoints_new_access_profile = new_access_profile.checkpoints.all()
        if len(list_checkpoints_obj_from_BD) > len(list_checkpoints_new_access_profile):
            list_checkpoints_remove_card = [el for el in list_checkpoints_obj_from_BD if el not in list_checkpoints_new_access_profile]
            signal_del_card = DEL_CARDS(card_number=old_pass_number)
            list_controllers = get_list_controllers(list_checkpoints=list_checkpoints_remove_card)
            give_signal_to_controllers(list_controllers=list_controllers, signal=signal_del_card)
            return (f'Сужение профиля доступа --> удаление пропуска: {request_pass_number}({new_pass_number}) из {list_controllers}', 0)
            return new_pass_number

        elif len(list_checkpoints_obj_from_BD) < len(list_checkpoints_new_access_profile):
            list_checkpoints_add_card = [el for el in list_checkpoints_new_access_profile if el not in list_checkpoints_obj_from_BD]
            signal_add_card = ADD_CARD(card_number=new_pass_number)
            list_controllers = get_list_controllers(list_checkpoints=list_checkpoints_add_card)
            give_signal_to_controllers(list_controllers=list_controllers, signal=signal_add_card)
            return (f'Расширение профиля доступа --> запись пропуска: {request_pass_number}({new_pass_number}) в {list_controllers}', 0)
            return new_pass_number

        else:
            list_checkpoints_remove_card = [el for el in list_checkpoints_obj_from_BD if el not in list_checkpoints_new_access_profile]
            list_checkpoints_add_card = [el for el in list_checkpoints_new_access_profile if el not in list_checkpoints_obj_from_BD]
            signal_del_card = DEL_CARDS(card_number=old_pass_number)
            signal_add_card = ADD_CARD(card_number=new_pass_number)
            list_controllers_for_del_card = get_list_controllers(list_checkpoints=list_checkpoints_remove_card)
            list_controllers_for_add_card = get_list_controllers(list_checkpoints=list_checkpoints_add_card)
            give_signal_to_controllers(list_controllers=list_controllers_for_del_card, signal=signal_del_card)
            give_signal_to_controllers(list_controllers=list_controllers_for_add_card, signal=signal_add_card)
            return (f'''Изменение профиля доступа --> удаление пропуска: {request_pass_number}({new_pass_number}) из {list_controllers_for_del_card}
            ||| --> запись пропуска:{request_pass_number}({new_pass_number}) в {list_controllers_for_add_card}''', 0)
            return new_pass_number

    if change_access_profile == True and change_pass_number == True:
        new_access_profile = AccessProfile.objects.get(pk=request_access_profile)
        list_checkpoints_new_access_profile = new_access_profile.checkpoints.all()
        print(f'list_checkpoints_new_access_profile -->> {list_checkpoints_new_access_profile}')

        try:
            print('try 1')
            list_controllers_for_del_card = get_list_controllers(list_checkpoints=list_checkpoints_obj_from_BD)
            print(f'list_controllers_for_del_card -->> {list_controllers_for_del_card}')
            signal_del_card = DEL_CARDS(card_number=old_pass_number)
            give_signal_to_controllers(list_controllers=list_controllers_for_del_card, signal=signal_del_card)
        except Exception as e:
            pass
            print(f'--e--->> {e}')
        try:
            print('try 2')
            list_controllers_add_card = get_list_controllers(list_checkpoints=list_checkpoints_new_access_profile)
            print(f'list_controllers_add_card -->> {list_controllers_add_card}')
            signal_add_card = ADD_CARD(card_number=new_pass_number)
            give_signal_to_controllers(list_controllers=list_controllers_add_card, signal=signal_add_card)
        except Exception as e:
            pass
            print(f'--e--->> {e}')
        return f'Записываю карту {request_pass_number}({new_pass_number}) на контроллеры: {list_controllers_add_card}. Профиль: {new_access_profile}', 0

