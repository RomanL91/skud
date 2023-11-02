import asyncio

from django.core.management.base import BaseCommand

from core.settings import env

id_bot = env("BOT_ID")

if id_bot:
    from app_telegram.main import bot, dp


    async def main():
        await dp.start_polling(bot)


class Command(BaseCommand):
    id_bot = env("BOT_ID")

    def handle(self, *args, **options):
        if self.id_bot:
            print('[==INFO==] Запуск TELEGRAM BOTA!')
            asyncio.run(main())
