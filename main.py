import time
from fastapi import FastAPI, Request
from admin.views import UsersAdmin, HotelsAdmin, RoomsAdmin, BookingsAdmin
from bookings.router import router as router_bookings
from config import settings
from database import engine
from logger import logger
import sentry_sdk
from pages.router import router as router_pages
from users.router import router_auth, router_users
from hotels.router import router as router_hotels
from upload_images.router import router as router_upload_images
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
# from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from sqladmin import Admin
from admin.auth import authentication_backend
import uvicorn

sentry_sdk.init(
    dsn="https://3ee5fa27194a2fc50569bb9970a18ea3@o4506003606339584.ingest.sentry.io/4506003610992640",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI(title="Бронирование Отелей", version="1.0", root_path="/api")

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
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

# Подключение версионирования
app = VersionedFastAPI(app, version_format='{major}', prefix_format='/api/v{major}')

# Подключение админки
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

app.mount("/static", StaticFiles(directory="static"), "static")


@app.on_event("startup")
def startup():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={"process_time": round(process_time, 4)})
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
