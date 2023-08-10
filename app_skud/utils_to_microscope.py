import requests, json, base64, environ, re
from django.contrib import messages
from core.settings import BASE_DIR, MEDIA_URL


env = environ.Env()
env.read_env('.env')

URL_SDK = env('URL_SDK')
URL_API = env('URL_API')

CONFIGEX_MICRPSCOPE = 'configex?responsetype=json'
ARCHIVEEVENTS = 'specialarchiveevents?startTime=<START>&endTime=<END>&eventid=427f1cc3-2c2f-4f50-8865-56ae99c3610d&channelid=<ID_CAM>'

POST_ADD_GRP_PREF = 'faces-groups?&module=complete'
POST_UPDATE_GRP_PREF = 'faces-groups/<ID>?module=complete'

POST_ADD_FACE_PREF = 'faces?module=complete'
PUT_UPDATE_FACE_PREF = 'faces/<ID>?module=complete'
DELETE_FACE_PREF = 'faces/<ID>?module=complete'
GET_ID_FACE_MICROSCOPE = "faces?module=complete&filter=external_id=<ID>"

login=env('LOGIN')
passw=env('PASSWORD')


def commands_RESTAPI_microscope(
        url: str, 
        login: str, 
        passw: str, 
        method: str, 
        point: str = None, 
        data: dict = None) -> dict | None: 
    try:
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
    except: pass


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
        mask_data_for_microscope['groups'][0]['id'] = obj.department.data_departament["body_response"]['id']
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


def list_choise_camera(list_id_camera_microscope):
    try:
        return ((i["Name"], i["Name"]) for i in list_id_camera_microscope["Channels"])
    except:
        return (('', ''),)


def get_name_id_camera_to_name_camera(name_camera, list_camera_from_microscope):
    return {f"{name_camera}": i["Id"] for i in list_camera_from_microscope["Channels"] if name_camera == i["Name"]}


def get_archiveevents_from_microscope(url_api_sdk, point, login, passw, time_start, time_end, id_cam_microscope):
    try:
        url = f'{url_api_sdk}{point}'.replace(
            '<START>', time_start).replace('<END>', time_end).replace('<ID_CAM>', id_cam_microscope)
        response_microscope = requests.get(url, auth=(login, passw), timeout=1).iter_lines(decode_unicode=True)
        list_external_id_from_microscope = []
        for el in response_microscope:
            if 'ExternalId' not in el:
                continue
            num_id = re.findall(r'\d*\.\d+|\d+', el)
            list_external_id_from_microscope.extend(num_id)
        print(f'list_external_id_from_microscope --->>> {list_external_id_from_microscope}')
        return list_external_id_from_microscope
    except: pass
