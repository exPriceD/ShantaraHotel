from flask import render_template, request, redirect, session, url_for, Response, Blueprint
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from app import db, login_manager
from app.models import Bookings, Details

import json

admins = Blueprint('admin', __name__)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


bookings = [
    {"id": 1, "name": "Александр", "dates": "20.04.2024 - 27.04.2024", "adults": 2, "children": 1,
     "phone": "+7 123 456 78 90", "email": "alex@example.com", "status": "Ожидает подтверждения"},
    {"id": 2, "name": "Мария", "dates": "22.04.2024 - 29.04.2024", "adults": 2, "children": 0,
     "phone": "+7 098 765 43 21", "email": "maria@example.com", "status": "Подтверждено"}
]


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@admins.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin":
            user = User(1)
            login_user(user)
            session.permanent = True
            return redirect(url_for("admin.admin"))
        return "Неверное имя пользователя или пароль"
    return render_template("admin/login.html")


@admins.route("/admin")
@login_required
def admin():
    return render_template("admin/admin.html", bookings=bookings)


@admins.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admins.route("/admin/bookings", methods=["GET"])
@login_required
def get_bookings():
    all_bookings = Bookings.query.all()
    bookings_with_details = []

    for booking in all_bookings:
        # Получаем связанные детали бронирования
        details = Details.query.filter_by(booking_id=booking.id).first()
        # Преобразуем объекты модели в словари
        booking_data = {
            'id': booking.id,
            'entry_date': booking.entry_date,
            'departure_date': booking.departure_date,
            'status': booking.status,
            'booking_date': booking.booking_date,
            'details': {
                'name': details.name,
                'adults': details.adults,
                'children': details.children,
                'phone': details.phone,
                'email': details.email,
                'admin_comment': details.admin_comment.strip()
            } if details else {}
        }

        bookings_with_details.append(booking_data)

    response = {
        "status": 200,
        "bookings": bookings_with_details
    }
    print(response)
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/confirm/<int:booking_id>", methods=['POST'])
@login_required
def confirm(booking_id):
    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/cancel/<int:booking_id>", methods=['POST'])
@login_required
def cancel(booking_id):
    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/add-comment/<int:booking_id>", methods=['POST'])
@login_required
def add_comment(booking_id):
    comment = request.json["comment"]

    booking_details = Details.query.filter_by(booking_id=booking_id).first()
    booking_details.admin_comment = comment

    db.session.add(booking_details)
    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')