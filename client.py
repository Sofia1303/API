from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QLineEdit, QTextEdit, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
import sys
import requests
import re

API_URL = "http://127.0.0.1:8000"


class ReviewsWindow(QWidget):
    def __init__(self, token, place_id=None):
        super().__init__()
        self.token = token
        self.place_id = place_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Отзывы")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        self.reviews_label = QLabel("Отзывы о месте:")
        layout.addWidget(self.reviews_label)

        self.reviews_list = QTextEdit()
        self.reviews_list.setReadOnly(True)
        layout.addWidget(self.reviews_list)

        self.load_reviews()

        self.setLayout(layout)

    def load_reviews(self):
        response = requests.get(
            f"{API_URL}/reviews/{self.place_id}", headers={"Authorization": f"Bearer {self.token}"})
        if response.status_code == 200:
            reviews = response.json()
            self.reviews_list.setText("\n\n".join(
                [f"{"Пользователь "}{r['user_id']}: {r['rating']}\n{r['comment']}" for r in reviews]))
        else:
            self.reviews_list.setText("Не удалось загрузить отзывы.")


class RegistrationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация")
        self.setGeometry(200, 200, 300, 200)
        self.setWindowOpacity(0.9)

        layout = QVBoxLayout()
        self.setWindowFlags(Qt.WindowType.Window |
                            Qt.WindowType.FramelessWindowHint)

        self.label = QLabel("Введите логин:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.label = QLabel("Введите email:")
        layout.addWidget(self.label)

        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()

        response = requests.post(
            f"{API_URL}/register/",
            json={"username": username, "email": email, "password": password}
        )

        if response.status_code == 201:
            self.status_label.setText("Регистрация успешна!")
            self.close()
        else:
            error_message = response.json().get("detail", "Ошибка регистрации!")
            self.status_label.setText(error_message)


class BookingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.token = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Система бронирования")
        self.setGeometry(100, 100, 500, 500)

        layout = QVBoxLayout()

        self.label = QLabel("Введите логин:")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.open_registration)
        layout.addWidget(self.register_button)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.hide()
        layout.addWidget(self.logout_button)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.load_button = QPushButton("Загрузить места")
        self.load_button.clicked.connect(self.load_places)
        layout.addWidget(self.load_button)

        self.days_label = QLabel("Количество дней бронирования:")
        layout.addWidget(self.days_label)

        self.days_input = QSpinBox()
        self.days_input.setRange(1, 30)
        layout.addWidget(self.days_input)

        self.book_button = QPushButton("Забронировать")
        self.book_button.clicked.connect(self.book_place)
        layout.addWidget(self.book_button)

        self.payment_label = QLabel("Выберите бронирование для оплаты:")
        layout.addWidget(self.payment_label)

        self.booking_dropdown = QComboBox()
        layout.addWidget(self.booking_dropdown)

        self.load_bookings_button = QPushButton("Загрузить бронирования")
        self.load_bookings_button.clicked.connect(self.load_bookings)
        layout.addWidget(self.load_bookings_button)

        self.cancel_booking_button = QPushButton("Отменить бронирование")
        self.cancel_booking_button.clicked.connect(self.cancel_booking)
        layout.addWidget(self.cancel_booking_button)

        self.payment_button = QPushButton("Оплатить бронирование")
        self.payment_button.clicked.connect(self.process_payment)
        layout.addWidget(self.payment_button)

        self.review_label = QLabel("Оставить отзыв:")
        layout.addWidget(self.review_label)

        self.place_dropdown = QComboBox()
        layout.addWidget(self.place_dropdown)

        self.review_input = QTextEdit()
        layout.addWidget(self.review_input)

        self.rating_input = QSpinBox()
        self.rating_input.setRange(1, 5)
        layout.addWidget(self.rating_input)

        self.review_button = QPushButton("Оставить отзыв")
        self.review_button.clicked.connect(self.leave_review)
        layout.addWidget(self.review_button)

        self.reviews_button = QPushButton("Все отзывы")
        self.reviews_button.clicked.connect(self.open_reviews)
        layout.addWidget(self.reviews_button)

        self.setLayout(layout)

    def open_reviews(self):
        selected = self.place_dropdown.currentText()
        match = re.search(r'\d+', selected)
        if match:
            place_id = int(match.group())
        self.reviews_window = ReviewsWindow(self.token, place_id=place_id)
        self.reviews_window.show()

    def cancel_booking(self):
        selected = self.booking_dropdown.currentText()
        if not selected:
            self.label.setText("Выберите бронирование!")
            return

        match = re.search(r'\d+', selected)
        if match:
            booking_id = int(match.group())
        else:
            print("Ошибка: не удалось извлечь ID бронирования")

        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(
            f"{API_URL}/cancel_booking/{booking_id}/", headers=headers)

        if response.status_code == 200:
            self.label.setText("Бронирование отменено!")
        else:
            self.label.setText("Ошибка при отмене бронирования!")

    def open_registration(self):
        self.registration_window = RegistrationWindow(self)
        self.registration_window.show()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        response = requests.post(
            f"{API_URL}/login/", json={"username": username, "password": password})
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.label.setText(f"Добро пожаловать, {username}!")

            self.login_button.hide()
            self.register_button.hide()
            self.username_input.hide()
            self.password_input.hide()
            self.logout_button.show()
        else:
            self.label.setText("Ошибка входа!")

    def logout(self):
        self.token = None
        self.label.setText("Вы вышли из системы.")

        self.login_button.show()
        self.register_button.show()
        self.logout_button.hide()

    def load_places(self):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        response = requests.get(f"{API_URL}/places/", headers=headers)
        if response.status_code == 200:
            places = response.json()
            self.list_widget.clear()
            self.place_dropdown.clear()
            for place in places:
                self.list_widget.addItem(
                    f"{place['id']} - {place['name']} ({place['location']}) - {place['price_per_day']} $/день")
                self.place_dropdown.addItem(
                    f"{place['id']} - {place['name']} ({place['location']})")

    def book_place(self):
        if not self.token:
            self.label.setText("Сначала войдите в систему!")
            return

        selected = self.list_widget.currentItem()
        if not selected:
            self.label.setText("Выберите место!")
            return

        place_id = int(selected.text().split(" - ")[0])
        days = self.days_input.value()
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{API_URL}/book/", json={"place_id": place_id,
                                 "start_date": start_date, "end_date": end_date}, headers=headers)

        if response.status_code == 200:
            self.label.setText("Бронирование успешно!")
        else:
            self.label.setText("Ошибка бронирования!")

    def load_bookings(self):
        if not self.token:
            self.label.setText("Сначала войдите в систему!")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/my_bookings/", headers=headers)

        if response.status_code == 200:
            bookings = response.json()
            self.booking_dropdown.clear()

            for booking in bookings:
                booking_id = booking.get("id", "Нет ID")

                start_date_str = booking.get("start_date")
                end_date_str = booking.get("end_date")
                status = booking.get("status")
                if not start_date_str or not end_date_str:
                    continue

                try:
                    start_date = datetime.fromisoformat(start_date_str)
                    end_date = datetime.fromisoformat(end_date_str)
                    num_days = (end_date - start_date).days
                except ValueError:
                    print(
                        f"Ошибка даты в бронировании {booking_id}: {start_date_str} - {end_date_str}")
                    continue

                place_id = booking.get("place_id")
                if not place_id:
                    price_per_day = 0
                else:
                    place_response = requests.get(
                        f"{API_URL}/places/{place_id}", headers=headers)
                    if place_response.status_code == 200:
                        place_data = place_response.json()
                        price_per_day = place_data.get("price_per_day", 0)
                    else:
                        price_per_day = 0

                booking_amount = num_days * price_per_day

                self.booking_dropdown.addItem(
                    f"Бронь {booking_id}, {num_days} дней, сумма: {booking_amount} $, статус: {status}",
                    userData={"id": booking_id,
                              "price_per_day": price_per_day, "num_days": num_days, "status": status}
                )
        else:
            self.label.setText("Ошибка загрузки бронирований!")

    def process_payment(self):
        if not self.token:
            self.label.setText("Сначала войдите в систему!")
            return

        selected_booking = self.booking_dropdown.currentData()
        if not selected_booking:
            self.label.setText("Выберите бронирование!")
            return

        booking_id = selected_booking["id"]
        price_per_day = selected_booking["price_per_day"]
        num_days = selected_booking["num_days"]
        total_price = price_per_day * num_days

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{API_URL}/pay/",
            json={"booking_id": booking_id, "amount": total_price},
            headers=headers
        )

        if response.status_code == 200:
            self.label.setText(f"Оплата успешна! Сумма: {total_price} $")
        elif response.status_code == 400:
            self.label.setText(
                "Ошибка оплаты! Бронирование уже оплачено или отменено.")
        else:
            self.label.setText(f"Ошибка оплаты: {response.text}")

    def leave_review(self):
        if not self.token:
            self.label.setText("Сначала войдите в систему!")
            return

        selected = self.place_dropdown.currentText()
        if not selected:
            self.label.setText("Выберите место!")
            return

        place_id = int(selected.split(" - ")[0])
        rating = self.rating_input.value()
        comment = self.review_input.toPlainText()
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.post(f"{API_URL}/review/", json={
            "place_id": place_id,
            "rating": rating,
            "comment": comment
        }, headers=headers)

        if response.status_code == 200:
            self.label.setText("Отзыв оставлен!")
        else:
            self.label.setText("Ошибка при отправке отзыва!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookingApp()
    window.show()
    sys.exit(app.exec())
