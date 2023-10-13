import environ, requests, json, time

from celery import shared_task

from django.core.cache import cache
from core.celery import app

from app_camera.models import Camera

from app_controller.models import Controller
from app_controller.views import ResponseModel


# DRY-юшки....
# как есть - работает брат =))))


env = environ.Env()
env.read_env('.env')

@shared_task(ignore_result=True)
def say(some):
    print(f'say --->>> {some}')
    return some


@shared_task(ignore_result=True)
def http_long_macroscope(channel_id_macroscope):
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

    cache_time = int(env('CACHE_TIME'))

    url = f"{env('URL_SDK')}event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid={channel_id_macroscope}&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    response = requests.get(url, stream=True, timeout=7)

    with open('celery', 'rb') as fd:
        try:
            for chunk in response.iter_content(decode_unicode=True, chunk_size=10000000):
                if 'ExternalId' in chunk:
                    line = chunk.splitlines()
                    external_id = line[23]
                    _, external_id = external_id.split(':')
                    external_id = external_id.strip(' ",')
                    print(f'[==INFO==] Получен внешний ID: {external_id} от канала: {channel_id_macroscope}' )
                    if external_id != '':
                        cache.set(external_id, int(external_id), timeout=cache_time)
                elif 'ExternalId' not in chunk:
                    try:
                        comment = chunk.splitlines()[-2]
                    except: continue
                    if comment != '\t"Comment" : "KeepAlive"':
                        continue
                    print(f'[==INFO==] Сигнал от --->>> {channel_id_macroscope} === {time.time()}')
                    cache.set(channel_id_macroscope, True, timeout=3)
                    stat_check = check(channel_id_macroscope)
                    if stat_check != True:
                        print(f'[==ERROR==] Статус камеры --->>> {stat_check}')
                        response.close()
                        try:
                            camera_off = Camera.objects.get(id_camera_microscope=channel_id_macroscope)
                            id_process = camera_off.other_data_camera[camera_off.id_camera_microscope]
                        except Exception as e:
                            print(f'[==ERROR==] --->>> {e}')
                        ff.delay(channel_id_macroscope, list_message)
                        app.control.revoke(id_process, terminate=True)
        except Exception as e:
            print(f'[==ERROR==] Обрыв HTTP_long c {channel_id_macroscope}')
            print(f'[==ERROR==] --->>> {e}')
            response.close()
            try:
                camera_off = Camera.objects.get(id_camera_microscope=channel_id_macroscope)
                id_process = camera_off.other_data_camera[camera_off.id_camera_microscope]
            except Exception as e:
                print(f'[==ERROR==] --->>> {e}')
            ff.delay(channel_id_macroscope, list_message)
            app.control.revoke(id_process, terminate=True)


@shared_task(ignore_result=True)
def checking_HTTP_LONG_connection_with_macroscope(id_camera_microscope):
    if Camera.objects.all().count() == 0:
        return None
    count = 0
    print(f'=== checking_HTTP_LONG_connection_with_ {id_camera_microscope} ===')
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
    while True:
        count += 1
        print(f'=== checking_HTTP_LONG_connection_with_ {id_camera_microscope} === {count}')
        try:
            stat_check = check(id_camera_microscope)
            if stat_check:
                camera = Camera.objects.get(id_camera_microscope=id_camera_microscope)
                list_controllers = [
                    Controller.objects.get(serial_number=int(el.split(' ')[-1])) for el in camera.other_data_camera['controllers'] 
                ]
                for controller in list_controllers:
                    list_message[0]['online'] = 1
                    list_message[1]['mode'] = 1
                    controller.controller_online = 1
                    controller.controller_mode = 1
                    data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                    data = json.dumps(data)
                    try:
                        id_process = str(http_long_macroscope.delay(id_camera_microscope))
                        camera.other_data_camera[id_camera_microscope] = id_process
                        camera.save()
                        response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data, timeout=20)
                        print(f'[==INFO==] Контроллер {controller} переведен в 2 факторный режим')
                        controller.save()
                    except Exception as e:
                        print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 2 факторный режим')
                        print(f'[==ERROR==] --->>> {e}')
                        continue
                print(f'[==INFO==] Камера {camera} доступна системе')
                return None
            else:
                time.sleep(1)
                continue
        except:
            time.sleep(1)
            continue
        

@shared_task(ignore_result=True)
def ff(channel_id_macroscope, list_message):
    print(f'[==INFO==] Пуск аварийной функции!')
    try:
        camera_off = Camera.objects.get(id_camera_microscope=channel_id_macroscope)
    except Exception as e:
        print(f'[==ERROR==] Камера с id {channel_id_macroscope} не найдена!')
        print(f'[==ERROR==] --->>> {e}')
        camera_off = None
    if camera_off == None:
        print(f'[==ERROR==] Камеры {channel_id_macroscope} нет в системе!')
        return None
    list_controllers_switching_to_single_factor_mode = [
        Controller.objects.get(serial_number=int(el.split(' ')[-1])) for el in camera_off.other_data_camera['controllers'] 
    ]
    for controller in list_controllers_switching_to_single_factor_mode:
        list_message[0]['online'] = 0
        list_message[1]['mode'] = 0
        controller.controller_online = 0
        controller.controller_mode = 0
        data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
        data = json.dumps(data)
        try:
            response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data, timeout=20)
            print(f'[==INFO==] Контроллер {controller} переведен в 1 факторный режим')
            controller.save()
        except Exception as e:
            print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 1 факторный режим')
    checking_HTTP_LONG_connection_with_macroscope.delay(channel_id_macroscope)


def check(id_camera_microscope):
    url_status_camera = f"{env('URL_SDK')}api/channels/{id_camera_microscope}/status"
    try:
        response = requests.get(url_status_camera, auth=(env('LOGIN'), env('PASSWORD')), timeout=1)
        json_response = response.json()
        status_cam = json_response['Status']
        if status_cam == 'Ok':
            return True
        return False
    except:
        return False
