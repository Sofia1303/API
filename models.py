from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    pending = "pending"
    canceled = "canceled"


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    pending = "pending"
    failed = "failed"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    location = Column(String)
    description = Column(String)
    price_per_day = Column(Float)

    bookings = relationship("Booking", back_populates="place")
    reviews = relationship("Review", back_populates="place")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    place_id = Column(Integer, ForeignKey("places.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)

    user = relationship("User", back_populates="bookings")
    place = relationship("Place", back_populates="bookings")
    payment = relationship("Payment", uselist=False, back_populates="booking")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Float)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    timestamp = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    place_id = Column(Integer, ForeignKey("places.id"))
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")


# psql -U booking_user -d booking_db -c "SELECT * FROM reviews; SELECT * FROM payments; SELECT * FROM bookings; SELECT * FROM places; SELECT * FROM users;"
