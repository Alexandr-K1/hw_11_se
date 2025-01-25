import logging
from datetime import date, timedelta

from sqlalchemy import select, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.user_id == user.id).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    try:
        stmt = select(Contact).filter(Contact.email == body.email, Contact.user_id == user.id)
        existing_contact = await db.execute(stmt)
        if existing_contact.scalar_one_or_none():
            raise ValueError("Email already exists")

        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except Exception as err:
        logger.error(f"Error creating contact in repository: {err}")
        raise


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        logger.warning(f"Contact with ID {contact_id} for user {user.id} not found.")
        return None

    if body.email:
        stmt = select(Contact).filter(Contact.email == body.email, Contact.id != contact_id,
                                      Contact.user_id == user.id)
        existing_contact = await db.execute(stmt)
        if existing_contact.scalar_one_or_none():
            raise ValueError("Email already exists")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        logger.warning(f"Contact with ID {contact_id} for user {user.id} not found.")
        return None
    await db.delete(contact)
    await db.commit()
    return contact


async def search_contact(first_name: str | None, last_name: str | None, email: str | None, db: AsyncSession,
                         user: User):
    stmt = select(Contact).filter(Contact.user_id == user.id)
    if first_name:
        stmt = stmt.filter(Contact.first_name.ilike(f'%{first_name}%'))
    if last_name:
        stmt = stmt.filter(Contact.last_name.ilike(f'%{last_name}%'))
    if email:
        stmt = stmt.filter(Contact.email.ilike(f'%{email}%'))
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_birthday(today: date, db: AsyncSession, user: User):
    start_date = today
    end_date = start_date + timedelta(days=7)
    start_month, start_day = start_date.month, start_date.day
    end_month, end_day = end_date.month, end_date.day

    logger.info(f"Searching for contacts with birthdays between {start_date} and {end_date}")

    if start_month == 12 and end_month == 1:
        stmt = select(Contact).filter(
            and_(
                Contact.user_id == user.id,
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
        )
    else:
        stmt = select(Contact).filter(
            and_(
                Contact.user_id == user.id,
                extract('month', Contact.birthday) == start_month,
                or_(
                    extract('day', Contact.birthday) >= start_day,
                    extract('day', Contact.birthday) <= end_day,
                )
            )
        )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    logger.info(f"Found {len(contacts)} contacts with upcoming birthdays")
    return contacts
