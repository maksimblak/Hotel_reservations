from fastapi import APIRouter, Depends, Response

from exceptions import CannotAddDataToDatabase, UserAlreadyExistsException
from models import Users
from users.auth import authenticate_user, create_access_token, get_password_hash
from users.dao import UserDAO
from users.dependencies import get_current_user
from users.schemas import SUserAuth

router_auth = APIRouter(prefix="/auth", tags=["Аутентификация"])
router_users = APIRouter(prefix="/users", tags=["Пользователи"])


# Регистрация нового пользователя
@router_auth.post("/register", status_code=201)
async def register_user(user_data: SUserAuth):
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    new_user = await UserDAO.add(email=user_data.email, hashed_password=hashed_password)
    if not new_user:
        raise CannotAddDataToDatabase


# Вход пользователя в систему и создание токена доступа
@router_auth.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.email, user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}


# Выход пользователя из системы и удаление токена доступа
@router_auth.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")


# Получение информации о текущем пользователе
@router_users.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user
