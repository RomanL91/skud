import requests, json
import base64
from django.contrib import messages
from core.settings import BASE_DIR, MEDIA_URL


URL_API = 'http://192.168.0.11:8080/api/'

POST_ADD_GRP_PREF = 'faces-groups?&module=complete'
POST_UPDATE_GRP_PREF = 'faces-groups/<ID>?module=complete'

POST_ADD_FACE_PREF = 'faces?module=complete'
PUT_UPDATE_FACE_PREF = 'faces/<ID>?module=complete'
DELETE_FACE_PREF = 'faces/<ID>?module=complete'
GET_ID_FACE_MICROSCOPE = "faces?module=complete&filter=external_id=<ID>"

login='zik'
passw='2af9b1ba42dc5eb01743e6b3759b6e4b'


def commands_RESTAPI_microscope(
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


def install_stock(request, obj, status):
    if status != 200:
        messages.error(request, 'Фото сотрудника НЕ добавлено в базу распознования лиц.')
        obj.employee_photo = 'no_foto.png'
        obj.data_staffs = {'microscope': False}
        obj.save()
    else:
        obj.data_staffs = {'microscope': True}
        messages.success(request, 'Фото сотрудника добавлено в базу распознования лиц.')
        obj.save()


def get_data_to_send_microscope(obj):
    path_image = f'{BASE_DIR}/{MEDIA_URL}{obj.employee_photo}'
    mask_data_for_microscope = {
        "external_id": "id",
        "first_name": "first_name",
        "patronymic": "patronymic",
        "second_name": "second_name",
        "additional_info": "position",
        "groups": [{"id": "id_microscope"}],
        "face_images": ['image_base64']
    }
    with open(path_image, 'rb') as file_image:
        encoded_string = base64.b64encode(file_image.read())
        mask_data_for_microscope['external_id'] = obj.pk
        mask_data_for_microscope['first_name'] = obj.first_name
        mask_data_for_microscope['patronymic'] = obj.patronymic
        mask_data_for_microscope['second_name'] = obj.last_name
        mask_data_for_microscope['additional_info'] = str(obj.position)
        mask_data_for_microscope['groups'][0]['id'] = obj.department.data_departament["id"]
        mask_data_for_microscope['face_images'] = [encoded_string.decode('UTF-8')]
    return mask_data_for_microscope


def microscope_work_with_faces(self, request, obj, form, change):
    response_microscope = commands_RESTAPI_microscope(
        url=URL_API,
        login=login,
        passw=passw,
        method='get',
        point=GET_ID_FACE_MICROSCOPE.replace('<ID>', f"'{obj.pk}'"),
    )
    total_count_face_from_microscope = response_microscope['body_response']['total_count']
    if total_count_face_from_microscope != 0:
        print('Update face microscope')
        id_microscope = response_microscope['body_response']['faces'][0]['id']
        data_for_microscope = get_data_to_send_microscope(obj=obj)
        response_microscope = commands_RESTAPI_microscope(
            url=URL_API, 
            login=login,
            passw=passw,
            method='put',
            point=PUT_UPDATE_FACE_PREF.replace('<ID>', id_microscope),
            data=data_for_microscope
        )
        if response_microscope['status_code'] != 200:
            install_stock(request=request, obj=obj, status=response_microscope['status_code'])
            response_microscope = commands_RESTAPI_microscope(
                url=URL_API, 
                login=login,
                passw=passw,
                method='delete',
                point=DELETE_FACE_PREF.replace('<ID>', id_microscope),
            )
        else:
            install_stock(request=request, obj=obj, status=response_microscope['status_code'])
    else:
        print('Create face microscope')
        data_for_microscope = get_data_to_send_microscope(obj=obj)
        response_microscope = commands_RESTAPI_microscope(
            url=URL_API, 
            login=login,
            passw=passw,
            method='post',
            point=POST_ADD_FACE_PREF,
            data=data_for_microscope
        )
        if response_microscope['status_code'] != 200:
            install_stock(request=request, obj=obj, status=response_microscope['status_code'])
        else:
            install_stock(request=request, obj=obj, status=response_microscope['status_code'])


