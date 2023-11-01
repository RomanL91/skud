from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey


class Base(DeclarativeBase): 
    pass


class TelegramPusher_Staffs(Base):
    __tablename__ = "app_telegram_telegrampusher_object_pusher"

    id = Column(Integer, primary_key=True, index=True)
    telegrampusher_id = Column(Integer(), ForeignKey("app_telegram_telegrampusher.id"))
    staffs_id = Column(Integer(), ForeignKey("app_skud_staffs.id"))


class TelegramPusher(Base):
    __tablename__ = "app_telegram_telegrampusher"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String)
    last_name = Column(Integer)
    first_name = Column(String)
    patronymic = Column(String)
    phone_number = Column(String)
    phone_number_status = Column(Boolean)
    object_pusher = relationship('Staffs', secondary='app_telegram_telegrampusher_object_pusher', backref='TelegramPusher')
    secret_pass = Column(String)
    secret_pass_status = Column(Boolean)
    status = Column(Boolean)


class Staffs(Base):
    __tablename__ = "app_skud_staffs"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(Integer)
    first_name = Column(String)
    patronymic = Column(String)
    phone_number = Column(String)
