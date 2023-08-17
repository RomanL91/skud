import threading
import requests
import json

from time import sleep

from django.core.management.base import BaseCommand


url = 'http://192.168.0.11:8080/event?login=zik&password=2af9b1ba42dc5eb01743e6b3759b6e4b&channelid=5cf30007-2663-45d8-83ff-008eb038e705&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json'

mira_out = '9d580c8a-59ef-4c6e-8cfd-cb7d58799d6f'

headers = {'Content-Length': 10000000, 'Transfer-Encoding': 'chunked', 'Connection': 'Keep-Alive'}

r = requests.get(url, stream=True)

class Command(BaseCommand):

    def printer(self):
        with open('ffff', 'rb') as fd:
            for chunk in r.iter_content(decode_unicode=True, chunk_size=10000000):
                print(chunk)
                if 'ExternalId' in chunk:
                    print('==== =ExternalId= ====')
                elif 'Comment' in chunk: 
                    print(f'==== =Comment= ====')
                ccc = chunk.splitlines()
                print(f'-ccc--->>> {ccc}')
                print('----------------------------------------------------------------------------------------')

    def handle(self, *args, **options):
        th = threading.Thread(target=self.printer)
        th.start()
        th.join()