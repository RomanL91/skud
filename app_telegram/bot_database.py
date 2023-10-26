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
    phone_number = f'+{phone_number}'
    print(f'phone_number --------------> {phone_number}')

    observer_telegram = session.query(TelegramPusher).filter(TelegramPusher.phone_number == phone_number).all()
    observer_telegram_count = session.query(TelegramPusher).count()
    print(f'observer_telegram --------------> {observer_telegram}')
    print(f'observer_telegram_count --------------> {observer_telegram_count}')

    for i in observer_telegram:
        print(f'i ---->>>> {i.phone_number}')

        if phone_number == i.phone_number:
            return 'НОМЕРА СОВПАДАЮТ'
        else:
            return 'НОМЕРА НЕ СОВПАДАЮТ'
        