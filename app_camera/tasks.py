import environ, requests

from celery import shared_task

from django.core.cache import cache

from app_controller.functions_working_database import get_external_id_from_cache



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
                print('==== =ExternalId= ====')
                line = chunk.splitlines()
                external_id = line[23]
                _, external_id = external_id.split(':')
                external_id = external_id.strip(' ",')
                if external_id != '':
                    cache.set(external_id, int(external_id), timeout=cache_time)
                    external_id_from_cache = get_external_id_from_cache(external_id)
                    print(f'-external_id_from_cache--->>> {external_id_from_cache}')

                print(f'-[line]--->>> {line}')
                print(f'-external_id--->>> {external_id}')
