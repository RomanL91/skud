from multiprocessing import Process

from django.core.management.base import BaseCommand

from app_camera.models import Camera


class Command(BaseCommand):

    def restart_HTTP_long_macroscope(self):
        list_cam = Camera.objects.all()
        print(f'[==INFO==] Список камер в системе: {list_cam}')
        for cam in list_cam:
            cam.save()


    def handle(self, *args, **options):
        print('[==INFO==] Запуск скрипта автоподключения HTTP_LONG!')
        proc = Process(target=self.restart_HTTP_long_macroscope)
        proc.start()
        proc.join()
        