from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from bot_model import (
    TelegramPusher, TelegramPusher_Staffs, Staffs
)


engine = create_engine("postgresql+psycopg2://postgres:password@postgres:5432/postgres", echo=True) #  IMPORT ENV
session = Session(bind=engine)


ffff = session.query(TelegramPusher).first()

print(f'fff --------------> {ffff}')
print(f'fff.object_pusher --------------> {ffff.object_pusher}')

for i in ffff.object_pusher:
    print(f'--------------->>>> {i.first_name}')