from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app_telegram.bot_model import (
    TelegramPusher, TelegramPusher_Staffs, Staffs
)


engine = create_engine("postgresql+psycopg2://postgres:password@postgres:5432/postgres", echo=True) #  IMPORT ENV
session = Session(bind=engine)


async def get_observer_telegram_pusher(session, phone_number, chat_id):
    phone_number = f'+{phone_number}'
    observer_telegram = session.query(TelegramPusher).filter(TelegramPusher.phone_number == phone_number).all()

    for i in observer_telegram:
        if phone_number == i.phone_number:
            i.chat_id = chat_id
            i.phone_number_status = True
            session.commit()
            return 'НОМЕРА СОВПАДАЮТ'
        else:
            return 'НОМЕРА НЕ СОВПАДАЮТ'
        

async def pass_valid(session, password):

    observer_telegram = session.query(TelegramPusher).filter(TelegramPusher.secret_pass == password).all()

    for i in observer_telegram:
        if i.phone_number_status:
            if password == i.secret_pass:
                i.secret_pass_status = True
                i.status = True
                session.commit()
                return 'ВЕРНЫЙ ПАРОЛЬ'
            else:
                return 'НЕ ВЕРНЫЙ ПАРОЛЬ'
        else:
            return 'ДЛЯ УСПЕШНОЙ АВТОРИЗАЦИИ СНАЧАЛА ПРЕДОСТАВЬТЕ НОМЕР ТЕЛЕФОНА'
    return 'НЕ ВЕРНЫЙ ПАРОЛЬ'
        