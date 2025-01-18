from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Date


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