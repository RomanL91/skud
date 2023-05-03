import requests, json

URL_API = 'http://192.168.0.11:8080/api/'
POST_ADD_GRP_PREF = 'faces-groups?&module=complete'
POST_UPDATE_GRP_PREF = 'faces-groups/<ID>?module=complete'

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
            print(response.status_code)
        case 'POST':
            response = requests.post(url, auth=(login, passw), data=data)
            return response.json()
        case 'PUT':
            response = requests.put(url, auth=(login, passw), data=data)
            return response.json()
        case 'DELETE':
            response = requests.delete(url, auth=(login, passw))
            return 
        case _ :
            return








