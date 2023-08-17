import environ, requests

from celery import shared_task


env = environ.Env()
env.read_env('.env')


@shared_task()
def http_long_macroscope():
    url = f"http://{env('URL_SDK')}/event?login={env('LOGIN')}&password={env('PASSWORD')}&channelid=9d580c8a-59ef-4c6e-8cfd-cb7d58799d6f&filter=427f1cc3-2c2f-4f50-8865-56ae99c3610d&responsetype=json"

    headers = {'Content-Length': 10000000, 'Transfer-Encoding': 'chunked', 'Connection': 'Keep-Alive'}

    r = requests.get(url, stream=True)
    with open('celery', 'rb') as fd:
        for chunk in r.iter_content(decode_unicode=True, chunk_size=10000000):
            print(chunk)
            if 'ExternalId' in chunk:
                print('==== =ExternalId= ====')
            elif 'Comment' in chunk: 
                print(f'==== =Comment= ====')
            ccc = chunk.splitlines()
            print(f'-ccc--->>> {ccc}')
            print('----------------------------------------------------------------------------------------')
