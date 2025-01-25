from datetime import datetime, timedelta
import logging

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users


ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Auth:

    pwt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoic2VjcmV0In0.9iLqI0y_B7t63CLMhdu0C0fSf-_e0ykc4pJv6oBjPPk'
    ALGORITHM = 'HS256'

    def verify_password(self, plain_password, hashed_password):
        return self.pwt_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password: str):
        return self.pwt_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

    async def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'score': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        logger.info(f"Access token created for user: {data.get('sub')}")
        return encoded_access_token

    async def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'score': 'refresh_token'})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        logger.info(f"Refresh token created for user: {data.get('sub')}")
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['score'] == 'refresh_token':
                logger.info(f"Valid refresh token for user: {payload['sub']}")
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError as err:
            logger.error(f"Invalid refresh token: {str(err)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            exp = payload.get('exp')
            if exp is None or datetime.utcnow() > datetime.utcfromtimestamp(exp):
                logger.warning(f"Token expired for user: {payload.get('sub')}")
                raise credentials_exception

            if payload['score'] != 'access_token':
                logger.warning("Invalid token scope detected")
                raise credentials_exception

            email = payload['sub']
            if email is None:
                logger.warning("Token missing 'sub' field")
                raise credentials_exception

        except JWTError as err:
            logger.error(f"Error decoding token: {str(err)}")
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            logger.warning(f"User not found for email: {email}")
            raise credentials_exception

        logger.info(f"User authenticated: {email}")
        return user

auth_service = Auth()