from fastapi import APIRouter, Depends
from pydantic import parse_obj_as
from bookings.schemas import SBooking, SNewBooking, SBookingInfo
from bookings.service import BookingDAO
from models import Users
from users.dependencies import get_current_user
from exceptions import RoomCannotBeBooked

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


# Получение списка бронирований для текущего пользователя
@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all_with_images(user_id=user.id)


# Создание нового бронирования
@router.post("", status_code=201)
async def add_booking(
        booking: SNewBooking,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )
    if not booking:
        raise RoomCannotBeBooked
    booking = parse_obj_as(SNewBooking, booking).dict()
    # Celery
    # send_booking_confirmation_email.delay(booking, user.email)

    return booking


# Удаление бронирования по его ид
@router.get("/{booking_id}")
async def remove_booking(
        booking_id: int,
        current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)
