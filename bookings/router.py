from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import parse_obj_as
from bookings.schemas import SBooking, SBookingInfo, SNewBooking
from bookings.service import BookingDAO
from models import Users
from users.dependencies import get_current_user
from exceptions import RoomCannotBeBooked

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all_with_images(user_id=user.id)


@router.post("", status_code=201)
async def add_booking(
        booking: SNewBooking,
        background_tasks: BackgroundTasks,
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
    # Background Tasks - встроено в FastAPI
    # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking


@router.get("/{booking_id}")
async def remove_booking(
        booking_id: int,
        current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)
