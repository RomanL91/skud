# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo

from django.core.management.base import BaseCommand
import threading


import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.session.aiohttp import AiohttpSession

# PROXY_URL = 'http://192.168.0.10:8080'


# session = AiohttpSession(proxy=PROXY_URL, ssl=False)
bot = Bot('6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo')

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# class Command(BaseCommand):
    

#     # def run_bot(self):
#     #     asyncio.run(main())


#     def handle(self, *args, **options):
#         # main()
#         th = threading.Thread(target=run_bot)
#         th.start()
#         th.join()
