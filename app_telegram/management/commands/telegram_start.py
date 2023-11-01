# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo

import asyncio

from django.core.management.base import BaseCommand

from app_telegram.main import bot, dp


async def main():
    await dp.start_polling(bot)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('[==INFO==] Запуск TELEGRAM BOTA!')
        asyncio.run(main())
