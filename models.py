from datetime import date
from pydantic import BaseModel
from sqlalchemy import Column, JSON, String, Date, Integer, ForeignKey, Computed
from sqlalchemy.orm import relationship

from database import Base


class Sbooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    booking = relationship("Bookings", back_populates="user")

    def __str__(self):
        return f"Пользователь {self.email}"


class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    rooms = relationship("Rooms", back_populates="hotel")

    def __str__(self):
        return f"Отель {self.name} {self.location[:30]}"


class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.id"))
    user_id = Column(ForeignKey("users.id"))
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))
    total_days = Column(Integer, Computed("date_to - date_from"))

    user = relationship("Users", back_populates="booking")
    room = relationship("Rooms", back_populates="booking")

    def __str__(self):
        return f"Booking #{self.id}"


class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False)
    hotel_id = Column(ForeignKey("hotels.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)

    hotel = relationship("Hotels", back_populates="rooms")
    booking = relationship("Bookings", back_populates="room")

    def __str__(self):
        return f"Номер {self.name}"

