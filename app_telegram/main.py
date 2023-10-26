
# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo

import asyncio, time
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_database import get_observer_telegram_pusher, session

bot = Bot('6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo')

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Регистрация"),],
        # [types.KeyboardButton(text="Без пюрешки")]
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


    await message.answer(f"""Спасибо, {contact.first_name}.\n
                         Ваш номер {contact.phone_number} был получен\n
                         answer_BD -->> {answer_BD}""",
                         reply_markup=types.ReplyKeyboardRemove())
    

@dp.message(F.text.lower() == "предоставить пароль")
async def with_puree(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 10):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(3)
    await message.answer(
        "Вводите пароль:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
