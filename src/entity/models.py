from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import String, Date, Integer, ForeignKey, func


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150))
    phone: Mapped[str] = mapped_column(String(15))
    birthday: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(250))

    user_id: Mapped[int] =mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user:Mapped['User'] =relationship('User', backref='contacts', lazy='joined')


class User(Base):
    __tablename__ ='users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', Date, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', Date, default=func.now(), onupdate=func.now())