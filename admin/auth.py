from typing import Optional

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from logger import logger
from users.auth import authenticate_user, create_access_token
from users.dependencies import get_current_user


class AdminAuth(AuthenticationBackend):
    # Аутентификация пользователя при входе в админку
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        user = await authenticate_user(email, password)
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})

        return True

    # Выход пользователя из админки и очистка сессии.
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    # Проверка аутентификации пользователя перед доступом к админке.
    # Если пользователь не аутентифицирован, он перенаправляется на страницу входа.
    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        user = await get_current_user(token)
        logger.debug(f"{user=}")
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


authentication_backend = AdminAuth(secret_key="...")
