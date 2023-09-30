from datetime import date
from typing import Optional
from fastapi import FastAPI, Query, Depends, Request


from models import Sbooking
from bookings.router import router as router_bookings
from pages.router import router as router_pages
from users.router import router_auth, router_users
from hotels.router import router as router_hotels
import uvicorn

app = FastAPI(
    title="Бронирование Отелей",
    version="1.0"
)
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_bookings)
app.include_router(router_pages)



@app.get('/bookings')
def add_booking(booking: Sbooking):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
