from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from bot_model import (
    TelegramPusher, TelegramPusher_Staffs, Staffs
)


engine = create_engine("postgresql+psycopg2://postgres:password@postgres:5432/postgres", echo=True) #  IMPORT ENV
session = Session(bind=engine)


ffff = session.query(TelegramPusher).first()
aaaa = session.query(TelegramPusher).filter(TelegramPusher.phone_number == '+77714648717').all()


print(f'fff --------------> {ffff}')
print(f'aaaa --------------> {aaaa} == {type(aaaa)}')



async def get_observer_telegram_pusher(session, phone_number):
    print(f'phone_number --------------> {phone_number}')
    observer_telegram = session.query(TelegramPusher).filter(TelegramPusher.phone_number == phone_number).all()
    observer_telegram_count = session.query(TelegramPusher).count()
    print(f'observer_telegram --------------> {observer_telegram}')
    print(f'observer_telegram_count --------------> {observer_telegram_count}')
    if observer_telegram_count == 1:
        phone_user_to_DB = observer_telegram[0].phone_number[-10:]
        phone_number = phone_number[-10:]
        if phone_number == phone_user_to_DB:
            return 'НОМЕРА СОВПАДАЮТ'
    else:
        return 'НОМЕРА НЕ СОВПАДАЮТ'
        