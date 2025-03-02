from fastapi import HTTPException, status
from fastapi import Depends
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import database
import auth
from auth import get_current_user
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class BookingCreate(BaseModel):
    place_id: int
    start_date: datetime
    end_date: datetime


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float


class ReviewCreate(BaseModel):
    place_id: int
    rating: int
    comment: str


@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(database.get_db)):
    if auth.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = auth.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()

    response = {"message": "User registered successfully"}
    print("API Response:", response)
    return response


@app.post("/login/", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected/")
def protected_route(user: models.User = Depends(get_current_user)):
    return {"message": f"Hello, {user.username}"}


@app.post("/book/")
def book_place(booking_data: BookingCreate, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    new_booking = models.Booking(
        user_id=user.id,
        place_id=booking_data.place_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        status="pending"
    )
    db.add(new_booking)
    db.commit()
    return {"message": "Booking request sent", "booking_id": new_booking.id}


@app.get("/my_bookings/")
def get_user_bookings(user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == user.id).all()
    return bookings


@app.post("/cancel_booking/{booking_id}")
def cancel_booking(booking_id: int, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id, models.Booking.user_id == user.id).first()
    if not booking:
        return {"error": "Booking not found"}
    booking.status = "canceled"
    payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id).first()
    if payment:
        db.delete(payment)
    db.commit()
    return {"message": "Booking cancelled"}


@app.post("/pay/")
def process_payment(payment_data: PaymentCreate, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    booking = db.query(models.Booking).filter(
        models.Booking.id == payment_data.booking_id, models.Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Booking is not pending")

    new_payment = models.Payment(
        booking_id=payment_data.booking_id,
        amount=payment_data.amount,
        status="paid"
    )
    booking.status = "confirmed"
    db.add(new_payment)
    db.commit()
    return {"message": "Payment successful", "payment_id": new_payment.id}


@app.post("/review/")
def leave_review(review_data: ReviewCreate, user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    new_review = models.Review(
        user_id=user.id,
        place_id=review_data.place_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(new_review)
    db.commit()
    return {"message": "Review submitted"}


@app.get("/reviews/{place_id}")
def get_reviews(place_id: int, db: Session = Depends(database.get_db)):
    reviews = db.query(models.Review).filter(
        models.Review.place_id == place_id).all()
    return reviews


@app.get("/places/")
def get_places(db: Session = Depends(database.get_db)):
    places = db.query(models.Place).all()
    return places


@app.get("/places/{place_id}")
def get_place(place_id: int, db: Session = Depends(database.get_db)):
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    return place
