# 6056863100:AAGPI62sHzm-c2wmEaOxFPU7Rq-bChMYAKo

import asyncio

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters.command import Command

from app_telegram.bot_database import get_observer_telegram_pusher, pass_valid, session


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
    chat_id = message.chat.id
    contact = message.contact
    answer_BD = await get_observer_telegram_pusher(session=session, phone_number=contact.phone_number, chat_id=chat_id)
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
    )


@dp.message(F.text)
async def extract_data(message: types.Message):
    data = {
        "code": "<N/A>"
    }
    kb = [
        [types.KeyboardButton(text="Предоставить контакт (тел.номер)", request_contact=True),],
        [types.KeyboardButton(text="Предоставить пароль"),],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    entities = message.entities or []
    if len(entities) != 0:
        for item in entities:
            if item.type in data.keys():

                data[item.type] = item.extract_from(message.text)

                answer_BD = await pass_valid(session=session, password=data['code'])

        if answer_BD == 'ВЕРНЫЙ ПАРОЛЬ':
            keyboard = types.ReplyKeyboardRemove()

        await message.reply(
            f"Ваш пароль: {html.quote(data['code'])}\nОтвет сервера \n-->> {answer_BD}",
            reply_markup=keyboard
        )
    else:
        pass
