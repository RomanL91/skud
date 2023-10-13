import threading, time

from django.core.management.base import BaseCommand

from app_camera.models import Camera
from app_camera.tasks import http_long_macroscope


class Command(BaseCommand):

    def restart_HTTP_long_macroscope(self):
        try:
            all_cameras = Camera.objects.all()
        except:
            all_cameras = None

        if all_cameras != None:
            for camera in all_cameras:
                id_camera_microscope = camera.id_camera_microscope
                id_process = str(http_long_macroscope.delay(id_camera_microscope))
                time.sleep(.5) # для наглядности выполениния
                try:
                    camera.other_data_camera[id_camera_microscope] = id_process
                except Exception as e:
                    print(f'[==ERROR==] Не удачный старт фоновой задачи HTTP_long c {camera}')
                    print(f'[==ERROR==] --->>> {e}')
                camera.save()
                print(f'[==INFO==] Camera: {camera.name} -->> Started <<--')


    def handle(self, *args, **options):
        th = threading.Thread(target=self.restart_HTTP_long_macroscope)
        th.start()
        th.join()