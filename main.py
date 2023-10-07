import time

import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin

from admin.auth import authentication_backend
from admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from bookings.router import router as router_bookings
from config import settings
from database import engine
from hotels.router import router as router_hotels
from logger import logger
from pages.router import router as router_pages
from upload_images.router import router as router_upload_images
from users.router import router_auth, router_users

# Инициализация Sentry для мониторинга ошибок
sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0, profiles_sample_rate=1.0)

app = FastAPI(title="Бронирование Отелей", version="1.0", root_path="/api")

# Подключение маршрутов FastAPI
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_bookings)
app.include_router(router_pages)
app.include_router(router_upload_images)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
# 3000 - порт, на котором работает фронтенд на React.js
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

# Подключение версионирования
app = VersionedFastAPI(app, version_format="{major}", prefix_format="/api/v{major}")

# Подключение админки
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

app.mount("/static", StaticFiles(directory="static"), "static")

# Подключение эндпоинта для отображения метрик для  сбора метрик Prometheus
instrumentator = Instrumentator(should_group_status_codes=False, excluded_handlers=[".*admin.*", "/metrics"])
instrumentator.instrument(app).expose(app)


# Функция, для инициализации клиента Redis
@app.on_event("startup")
def startup():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


# Middleware для замера времени обработки запросов
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info("Request handling time", extra={"process_time": round(process_time, 4)})
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
