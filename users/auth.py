from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from config import settings
from exceptions import IncorrectEmailOrPasswordException
from users.dao import UserDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Функция для создания хеша пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Функция для проверки пароля
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Функция для создания токена доступа
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


# Функция для аутентификации пользователя
async def authenticate_user(email: EmailStr, password: str):
    user = await UserDAO.find_one_or_none(email=email)
    if not (user and verify_password(password, user.hashed_password)):
        raise IncorrectEmailOrPasswordException
    return user
