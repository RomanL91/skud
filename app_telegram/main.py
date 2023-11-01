
# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo

import asyncio, time
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import html

from bot_database import get_observer_telegram_pusher, session

bot = Bot('6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo')

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Регистрация"),],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Здравствуйте! Пройдите регистрацию.", reply_markup=keyboard)


@dp.message(F.text.lower() == "регистрация")
async def with_puree(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Предоставить контакт (тел.номер)", request_contact=True),],
        [types.KeyboardButton(text="Предоставить пароль"),],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.reply("Приступим к регистрации. Предоставьте Боту данные: тел.номер и пароль.", reply_markup=keyboard)


@dp.message(F.contact)
async def get_contact(message: types.Message):
    contact = message.contact
    print(f'contact.phone_number ------>>>> {contact.phone_number}')
    answer_BD = await get_observer_telegram_pusher(session=session, phone_number=contact.phone_number)
    kb = [
        [types.KeyboardButton(text="Предоставить контакт (тел.номер)", request_contact=True),],
        [types.KeyboardButton(text="Предоставить пароль"),],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


    await message.answer(
        f"""Спасибо, {contact.first_name}.\nВаш номер {contact.phone_number} был получен\nответ сервера \n-->> {answer_BD}""",
                         reply_markup=keyboard)
    

@dp.message(F.text.lower() == "предоставить пароль")
async def with_puree(message: types.Message):
    
    await message.answer(
        "Вводите пароль моноширным шрифтом. \n\n Для этого введите `PASS` \n где PASS - Ваш пароль. \nОбратите внимание на знаки апострофа [`] до PASS и после - они обязательны!",
        # reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text)
async def extract_data(message: types.Message):
    data = {
        "code": "<N/A>"
    }
    entities = message.entities or []
    print(f'entities ----->>> {entities}')
    if len(entities) != 0:
        for item in entities:
            if item.type in data.keys():
                data[item.type] = item.extract_from(message.text)
        await message.reply(
            f"Ваш пароль: {html.quote(data['code'])}"
        )
    else:
        pass


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
