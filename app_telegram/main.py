
# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo


import asyncio, time, ssl
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.session import aiohttp

PROXY_URL = 'http://192.168.0.10:8080'

ses = aiohttp.ClientSession()
# session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
# session = AiohttpSession(proxy=PROXY_URL, ssl=False)
session = AiohttpSession(proxy=PROXY_URL, ssl=False)
# bot = Bot('6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo')
bot = Bot('6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo', session=session)

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@dp.message(Command("st"))
async def cmd_start(message: types.Message):
    count = 0
    while count < 10:
        await message.answer("Hello!")
        time.sleep(1)


async def main():
    async with aiohttp.ClientSession() as client:
        client.get(url='https://google.com', ssl=False)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())