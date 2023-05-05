import requests, json
from app_skud.forms import StaffsModelForm
import base64
from core.settings import BASE_DIR, MEDIA_URL

URL_API = 'http://192.168.0.11:8080/api/'

POST_ADD_GRP_PREF = 'faces-groups?&module=complete'
POST_UPDATE_GRP_PREF = 'faces-groups/<ID>?module=complete'

POST_ADD_FACE_PREF = 'faces?module=complete'

login='zik'
passw='2af9b1ba42dc5eb01743e6b3759b6e4b'


def commands_RESTAPI_microscope_for_operations_with_groups(
        url: str, 
        login: str, 
        passw: str, 
        method: str, 
        point: str = None, 
        data: dict = None) -> dict | None: 
    if data != None:
        data = json.dumps(data)
    url = f'{url}{point}'
    method = method.upper()    

    match method:
        case 'GET':
            response = requests.get(url, auth=(login, passw))
            return {'status_code': response.status_code, 'body_response': response.json()}
        case 'POST':
            response = requests.post(url, auth=(login, passw), data=data)
            return {'status_code': response.status_code, 'body_response': response.json()}
        case 'PUT':
            response = requests.put(url, auth=(login, passw), data=data)
            return {'status_code': response.status_code, 'body_response': response.json()}
        case 'DELETE':
            response = requests.delete(url, auth=(login, passw))
            return {'status_code': response.status_code, 'body_response': response.json()}
        case _ :
            return


from django.db.models.signals import post_save
from django.dispatch import receiver
from app_skud.models import Staffs

@receiver(post_save, sender=Staffs)
def send_foto_to_microscope(sender, instance, created, **kwargs):
    print(f'---sender--->>> {sender}')
    print(f'---instance--->>> {instance}')
    print(f'---instance.employee_photo--->>> {instance.employee_photo}')
    print(f'---kwargs--->>> {kwargs}')
    mask_data_for_microscope = {
                "external_id": "id",
                "first_name": "first_name",
                "patronymic": "patronymic",
                "second_name": "second_name",
                "additional_info": "position",
                "groups": [
                    {
                        "id": "id_microscope"
                    }
                ],
                "face_images": ['image_base64']
            }

    if instance.employee_photo != '' and created:
        print('пробую добавить фото------')
        path_image = f'{BASE_DIR}/{MEDIA_URL}{instance.employee_photo}'
        print(f'---path_image--->>> {path_image}')
        with open(path_image, 'rb') as file_image:
                encoded_string = base64.b64encode(file_image.read())
                mask_data_for_microscope['external_id'] = instance.pk
                mask_data_for_microscope['first_name'] = instance.first_name
                mask_data_for_microscope['patronymic'] = instance.patronymic
                mask_data_for_microscope['second_name'] = instance.last_name
                mask_data_for_microscope['additional_info'] = str(instance.position)
                mask_data_for_microscope['groups'][0]['id'] = instance.department.data_departament["id"]
                mask_data_for_microscope['face_images'] = [encoded_string.decode('UTF-8')]
        # print(f'---mask_data_for_microscope--->>> {mask_data_for_microscope}')
        response_to_microscope = commands_RESTAPI_microscope_for_operations_with_groups(
                url=URL_API, 
                login=login,
                passw=passw,
                method='post',
                point=POST_ADD_FACE_PREF,
                data=mask_data_for_microscope
            )
        print(f'---response_to_microscope--->>> {response_to_microscope}')
        if response_to_microscope['status_code'] != 200:
           pass
        #    '/admin/app_skud/staffs/115/change/'
    elif instance.employee_photo != '' and not created:
        print('изменение фото-----')
    else:
        print('не заливаем в макроскоп------')






