import environ, requests, time, json

from celery import shared_task

from django.core.cache import cache

from app_camera.models import Camera

from app_controller.views import ResponseModel


env = environ.Env()
env.read_env('.env')


@shared_task()
def http_long_macroscope(channel_id_macroscope):

    cache_time = int(env('CACHE_TIME'))

    url = f"{env('URL_SDK')}event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid={channel_id_macroscope}&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    response = requests.get(url, stream=True)

    with open('celery', 'rb') as fd:
        for chunk in response.iter_content(decode_unicode=True, chunk_size=10000000):
            if 'ExternalId' in chunk:
                line = chunk.splitlines()
                external_id = line[23]
                _, external_id = external_id.split(':')
                external_id = external_id.strip(' ",')
                if external_id != '':
                    cache.set(external_id, int(external_id), timeout=cache_time)


@shared_task()
def checking_HTTP_LONG_connection_with_macroscope():
    print('========= checking_HTTP_LONG_connection_with_macroscope ==========')
    all_cams = Camera.objects.all()
    if all_cams.count() == 0:
        return None
    cams_off = []
    controller_to_one_factor = []
    controller_to_two_factor = []
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
    for cam in all_cams:
        url_status = f"{env('URL_SDK')}api/channels/{cam.id_camera_microscope}/status"
        try:
            response = requests.get(url_status, auth=(env('LOGIN'), env('PASSWORD')))
            if response.status_code == 200:
                controller_to_two_factor.extend(
                    cam.checkpoint.controller_set.all()
                )
                controller_to_two_factor = set(controller_to_two_factor)
                    
                for controller in controller_to_two_factor:
                    if int(controller.controller_online) != 1 and int(controller.controller_mode) != 1:
                        list_message[0]['online'] = 1
                        list_message[1]['mode'] = 1
                        controller.controller_online = 1
                        controller.controller_mode = 1
                        controller.save()
                        data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                        data = json.dumps(data)
                        try:
                            response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data)
                            id_process = str(http_long_macroscope.delay(cam.id_camera_microscope))
                            cam.other_data_camera = {cam.id_camera_microscope: id_process}
                            cam.save()
                            print(f'[==INFO==] Контроллер {controller} переведен в 2 факторный режим')
                        except:
                            print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 2 факторный режим')
        except Exception as e:
            print(f'[==ERROR==] Сервер МАКРОСКОП {env("URL_SDK")} не доступен')
            cams_off.extend(all_cams)
        time.sleep(.2)

    if len(cams_off) > 0:
        for cam in cams_off: 
            controller_to_one_factor.extend(
                cam.checkpoint.controller_set.all()
            )
        
        for controller in controller_to_one_factor:
            if int(controller.controller_online) != 0 and int(controller.controller_mode) != 0:
                list_message[0]['online'] = 0
                list_message[1]['mode'] = 0
                controller.controller_online = 0
                controller.controller_mode = 0
                controller.save()
                data = ResponseModel(message_reply=list_message, serial_number_controller=controller.serial_number)
                data = json.dumps(data)
                try:
                    response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data)
                    print(f'[==INFO==] Контроллер {controller} переведен в 1 факторный режим')
                except Exception as e:
                    print(f'[==ERROR==] Не удалось перевести контроллер {controller} в 1 факторный режим')
                    for i in range(5):
                        try:
                            response_to_controller = requests.post(url=controller.other_data['controller_ip'], data=data)
                            print(f'[==INFO==] Контроллер {controller} переведен в 1 факторный режим')
                        except: pass
                        time.sleep(.5)
                time.sleep(.1)

