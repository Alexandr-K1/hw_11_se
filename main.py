import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes.contacts import router as contacts_router
from src.routes.auth import router as auth_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(auth_router)
app.include_router(contacts_router)


@app.get('/')
def index():
    return {'message': 'Contact Application'}

@app.get('/api/healthchecker')
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text('SELECT 1'))
        res = result.fetchone()
        if res is None:
            raise HTTPException(status_code=500, detail='Database is not configured correctly')
        return {"message": "Service is running!"}
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail='Database connection error')