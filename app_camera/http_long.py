import requests, aiohttp

import time, json, environ

from django.core.cache import cache

from app_camera.models import Camera

from app_controller.views import ResponseModel


env = environ.Env()
env.read_env('.env')

list_message = [
    {
    "id":123456789,
    "operation":"set_active",
    "active":1,
    "online":0
    }, 
    {
    "id":123456789,
    "operation":"set_mode",
    "mode": 0
    }
]


async def warning_f(channel_id_macroscope):
    try_counter = 1
    url = f"{env('URL_SDK')}event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid={channel_id_macroscope}&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    print(f'[==INFO==] Пуск аварийной функции!')
    try:
        camera_off = Camera.objects.get(id_camera_microscope=channel_id_macroscope)
    except Exception as e:
        print(f'[==ERROR==] Камера с id {channel_id_macroscope} не найдена!')
        print(f'[==ERROR==] --->>> {e}')
        return None
    # DRY
    list_controllers_switching_to_single_factor_mode = camera_off.controllers.all()
    for controller in list_controllers_switching_to_single_factor_mode:
        list_message[0]['online'] = 0
        list_message[1]['mode'] = 0
        controller.controller_online = 0
        controller.controller_mode = 0
        controller.save()
        data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
        data = json.dumps(data)
        try:
            response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data, timeout=20)
            print(f'[==INFO==] Контроллер {controller} переведен в 1 факторный режим')
            print(f'[==INFO==] Статус {response_to_controller.status_code}')
            controller.save()
        except Exception as e:
            print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 1 факторный режим')

    while True:
        time.sleep(2)
        try:
            response_to_http_long = requests.get(url, stream=True, timeout=7)
        except: 
            print(f'[==WARNING==] Сервер МАКРОСКОП не доступен!')
            continue
        if response_to_http_long.status_code != 200:
            print(f'[==WARNING==] Соединение с каналлом {channel_id_macroscope} нет. ПОПЫТКА --> {try_counter}')
            continue
        else:
            print(f'[==INFO==] Соединение с каналлом {channel_id_macroscope} УСТАНОВЛЕНО!')
            response_to_http_long.close()
            # DRY
            for controller in list_controllers_switching_to_single_factor_mode:
                list_message[0]['online'] = 1
                list_message[1]['mode'] = 1
                controller.controller_online = 1
                controller.controller_mode = 1
                data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                data = json.dumps(data)
                try:
                    response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data, timeout=20)
                    print(f'[==INFO==] Контроллер {controller} переведен в 2 факторный режим')
                    print(f'[==INFO==] Статус {response_to_controller.status_code}')
                    controller.save()
                except Exception as e:
                    print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 2 факторный режим')
            await main(channel_id_macroscope)
            break


async def main(channel_id_macroscope):
    print(f'====== STARTED HTTP_LONG WITH {channel_id_macroscope} ======')
    cache_time = int(env('CACHE_TIME'))
    url = f"{env('URL_SDK')}event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid={channel_id_macroscope}&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    timeout = aiohttp.ClientTimeout(sock_read=6)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as resp:
            
                with open('celery', 'rb') as fd:

                    async for chunk in resp.content.iter_chunked(1000000):

                        if b'ExternalId' in chunk:
                            print('==== =ExternalId= ====')
                            line = chunk.splitlines()
                            external_id = line[23]
                            external_id = external_id.decode('utf-8')
                            _, external_id = external_id.split(':')
                            external_id = external_id.strip(' ",')
                            print(f'[==INFO==] Получен внешний ID: {external_id}')
                            if external_id != '':
                                cache.set(external_id, int(external_id), timeout=cache_time)
                        elif b'ExternalId' not in chunk:
                            try:
                                comment = chunk.splitlines()[-2]
                            except: continue
                            if comment != b'\t"Comment" : "KeepAlive"':
                                continue
                            print(f'[==INFO==] CAMERA PING {channel_id_macroscope}')
                            cache.set(channel_id_macroscope, True, timeout=3)

        except Exception as e:
            print(f'[==ERROR==] Обрыв HTTP_long')
            print(f'e --->>> {e}')
            await warning_f(channel_id_macroscope)
