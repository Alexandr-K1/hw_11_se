from datetime import date, timedelta

from sqlalchemy import select, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()

async def create_contact(body: ContactSchema, db: AsyncSession):
    stmt = select(Contact).filter(Contact.email == body.email)
    existing_contact = await db.execute(stmt)
    if existing_contact.scalar_one_or_none():
        raise ValueError("Email already exists")

    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        if body.email:
            stmt = select(Contact).filter(Contact.email == body.email, Contact.id != contact_id)
            existing_contact = await db.execute(stmt)
            if existing_contact.scalar_one_or_none():
                raise ValueError("Email already exists")

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await db.commit()
        await db.refresh(contact)
    return contact

async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        return None
    await db.delete(contact)
    await db.commit()
    return contact

async def search_contact(first_name: str | None, last_name: str | None, email: str | None, db: AsyncSession):
    stmt = select(Contact)
    if first_name:
        stmt = stmt.filter(Contact.first_name.ilike(f'%{first_name}%'))
    if last_name:
        stmt = stmt.filter(Contact.last_name.ilike(f'%{last_name}%'))
    if email:
        stmt = stmt.filter(Contact.email.ilike(f'%{email}%'))
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_contact_birthday(today: date, db: AsyncSession):
    start_date = today
    end_date = start_date + timedelta(days=7)
    start_month, start_day = start_date.month, start_date.day
    end_month, end_day = end_date.month, end_date.day
    if start_month == 12 and end_month == 1:
        stmt = select(Contact).filter(
            or_(
                and_(
                    extract('month', Contact.birthday) == 12,
                    extract('day', Contact.birthday) >= start_day,
                ),
                and_(
                    extract('month', Contact.birthday) == 1,
                    extract('day', Contact.birthday) <= end_day,
                ),
            )
        )
    else:
        stmt = select(Contact).filter(
            and_(extract('month', Contact.birthday) == start_month,
                 extract('day', Contact.birthday) >= start_day,
                 extract('day', Contact.birthday) <= end_day,
                 )
        )
    result = await db.execute(stmt)
    return result.scalars().all()