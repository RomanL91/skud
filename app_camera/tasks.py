import environ, requests, json, time

from celery import shared_task

from django.core.cache import cache

from app_camera.models import Camera

from app_controller.views import ResponseModel


# DRY-юшки....

env = environ.Env()
env.read_env('.env')


@shared_task(ignore_result=True)
def http_long_macroscope(channel_id_macroscope):

    cache_time = int(env('CACHE_TIME'))

    url = f"{env('URL_SDK')}event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid={channel_id_macroscope}&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    response = requests.get(url, stream=True, timeout=7)

    with open('celery', 'rb') as fd:
        all_cams = Camera.objects.all() #получаю все камеры системы
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
                print(f'[==INFO==] Сигнал от --->>> {channel_id_macroscope} <<<---' )
                cache.set(f'camera - {channel_id_macroscope}', None, timeout=10)
        except Exception as e:
            pass_through_with_attached_controllers = {
                camera.checkpoint: camera.checkpoint.controller_set.all() for camera in all_cams 
            } # {<Checkpoint: вход на территорию>: <QuerySet [<Controller: Z5R Net 39705>, <Controller: Z5R Net 13080>]>}
            print(f'[==ERROR==] Потерян HTTP_LONG c {channel_id_macroscope}')
            print(f'[==ERROR==] --->>> {e}')
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
            if all_cams.count() == 0:
                print(f'[==INFO==] Камер в системе нет.')
                return None
            url_status = f"{env('URL_SDK')}api/channels/{channel_id_macroscope}/status"
            try:
                response = requests.get(url_status, auth=(env('LOGIN'), env('PASSWORD')), timeout=.3)
            except Exception as e:
                print(f'[==ERROR==] Камера {channel_id_macroscope} не доступна')
                try:
                    camera_off = all_cams.get(id_camera_microscope=channel_id_macroscope)
                    pass_for_transfer_to_single_factor_mode = camera_off.checkpoint
                except:
                    pass
                print(f'[==ERROR==] Камера {camera_off} не доступна')
                print(f'[==ERROR==] --->>> {e}')
                list_controllers_switching_to_single_factor_mode = \
                    pass_through_with_attached_controllers[pass_for_transfer_to_single_factor_mode]
                for controller in list_controllers_switching_to_single_factor_mode:
                    list_message[0]['online'] = 0
                    list_message[1]['mode'] = 0
                    controller.controller_online = 0
                    controller.controller_mode = 0
                    data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                    data = json.dumps(data)
                    try:
                        response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data)
                        print(f'[==INFO==] Контроллер {controller} переведен в 1 факторный режим')
                        controller.save()
                    except Exception as e:
                        print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 1 факторный режим')
                checking_HTTP_LONG_connection_with_macroscope.delay(channel_id_macroscope)


@shared_task(ignore_result=True)
def checking_HTTP_LONG_connection_with_macroscope(id_camera_microscope):
    print('========= checking_HTTP_LONG_connection_with_macroscope ==========')
    url_status_camera = f"{env('URL_SDK')}api/channels/{id_camera_microscope}/status"
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
        try:
            response = requests.get(url_status_camera, auth=(env('LOGIN'), env('PASSWORD')), timeout=.3)
            if response.status_code == 200:
                camera = Camera.objects.get(id_camera_microscope=id_camera_microscope)
                list_controllers = camera.checkpoint.controller_set.all()
                for controller in list_controllers:
                    if int(controller.controller_online) != 0 and int(controller.controller_mode) != 0: 
                        continue
                    list_message[0]['online'] = 1
                    list_message[1]['mode'] = 1
                    controller.controller_online = 1
                    controller.controller_mode = 1
                    data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                    data = json.dumps(data)
                    try:
                        response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data)
                        print(f'[==INFO==] Контроллер {controller} переведен в 2 факторный режим')
                        controller.save()
                        http_long_macroscope.delay(id_camera_microscope)
                    except Exception as e:
                        print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 2 факторный режим')
                        print(f'[==ERROR==] --->>> {e}')
                print(f'[==INFO==] Камера {camera} доступна системе')
                break
            else:
                time.sleep(1)
                continue
        except:
            time.sleep(1)
            continue
    