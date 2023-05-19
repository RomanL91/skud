from django.forms import ModelForm, ChoiceField

from app_camera.models import Camera
from app_skud.utils_to_microscope import (
    commands_RESTAPI_microscope, list_choise_camera,
    login, passw, URL_SDK, CONFIGEX_MICRPSCOPE)


response = commands_RESTAPI_microscope(
    url=URL_SDK, 
    login=login, 
    passw=passw, 
    method='get', 
    point=CONFIGEX_MICRPSCOPE
)


SELECT_DIRECTIONS =(
    ("ВХОД", "ВХОД"),
    ("ВЫХОД", "ВЫХОД"),
)

SELECT_CAMERA = list_choise_camera(list_id_camera_microscope=response['body_response'])


class CameraModelForm(ModelForm):
    name = ChoiceField(choices=SELECT_CAMERA)
    direction = ChoiceField(choices=SELECT_DIRECTIONS)
    def __init__(self, *args, **kwargs):
        super(CameraModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Camera
        exclude = (
            'id_camera_microscope',
        )