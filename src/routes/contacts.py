from datetime import date

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repositories_contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    try:
        contact = await repositories_contact.create_contact(body, db)
        return contact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get('/all', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contacts(limit, offset, db)
    return contacts

@router.get('/search', response_model=list[ContactResponse])
async def search_contact(first_name: str | None = Query(default=None, title='First Name'),
                         last_name: str | None = Query(default=None, title='Last Name'),
                         email: str | None = Query(default=None, title='Email'), db: AsyncSession = Depends(get_db)):
    if not any([first_name, last_name, email]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one search parameter must be provided")
    contacts = await repositories_contact.search_contact(first_name, last_name, email, db)
    return contacts

def get_today() -> date:
    return date.today()

@router.get('/birthdays', response_model=list[ContactResponse])
async def get_contact_birthday(today: date = Depends(get_today), db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contact_birthday(today, db)
    return contacts

@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contact.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact

@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    try:
        contact = await repositories_contact.update_contact(contact_id, body, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
        return contact
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contact.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    await repositories_contact.delete_contact(contact_id, db)
    return {'message': 'Contact deleted successfully'}

