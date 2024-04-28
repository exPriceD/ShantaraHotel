from flask import render_template, request, redirect, session, url_for, Response, Blueprint
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from app import db, login_manager
from app.models import Bookings, Details, Passports

from sqlalchemy import and_
import json

admins = Blueprint('admin', __name__)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


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
    return render_template("admin/admin.html")


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
        details = Details.query.filter_by(booking_id=booking.id).first()
        passports = Passports.query.filter_by(booking_id=booking.id).all()

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
            } if details else {},
            'passports': [
                {
                    'id': passport.id,
                    'booking_id': passport.booking_id,
                    'passport_number': passport.passport_number,
                    'fio': passport.fio,
                    'granted': passport.granted,
                    'granted_date': passport.granted_date,
                    'department_code': passport.department_code,
                    'gender': passport.gender,
                    'birth_date': passport.birth_date,
                    'birthplace': passport.birthplace,
                    'series': passport.series,
                    'number': passport.number,
                } for passport in passports
            ]
        }

        bookings_with_details.append(booking_data)

    bookings_with_details = list(reversed(bookings_with_details))

    response = {
        "status": 200,
        "bookings": bookings_with_details
    }
    print(response)
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/confirm/<int:booking_id>", methods=['POST'])
@login_required
def confirm(booking_id):
    booking = Bookings.query.get(booking_id)
    booking.status = "confirmed"

    db.session.add(booking)
    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/cancel/<int:booking_id>", methods=['POST'])
@login_required
def cancel(booking_id):
    booking = Bookings.query.get(booking_id)
    booking.status = "canceled"

    db.session.add(booking)
    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/end/<int:booking_id>", methods=['POST'])
@login_required
def end(booking_id):
    booking = Bookings.query.get(booking_id)
    booking.status = "ended"

    db.session.add(booking)
    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/update-booking/<int:booking_id>/<int:passport_number>", methods=['POST'])
@login_required
def add_comment(booking_id, passport_number):
    field_key = list(dict(request.json).keys())[0]
    field_value = request.json[field_key]

    if field_key in ["entry_date", "departure_date"]:
        booking = Bookings.query.get(booking_id)
        setattr(booking, field_key, field_value)
    elif field_key in ["name", "adults", "children", "phone", "email", "admin_comment"]:
        booking_details = Details.query.filter_by(booking_id=booking_id).first()
        setattr(booking_details, field_key, field_value)
    else:
        passport = Passports.query.filter(
            and_(Passports.booking_id == booking_id, Passports.passport_number == passport_number)
        ).first()
        setattr(passport, field_key, field_value)

    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/passport/<int:booking_id>/<int:passport_number>", methods=['DELETE'])
def del_passport(booking_id, passport_number):
    passport = Passports.query.filter(
        and_(Passports.booking_id == booking_id, Passports.passport_number == passport_number)
    ).first()

    if passport:
        db.session.delete(passport)
        db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/passport/<int:booking_id>/<int:passport_number>", methods=['POST'])
def add_passport(booking_id, passport_number):
    new_passport = Passports(booking_id=booking_id, passport_number=passport_number)

    db.session.add(new_passport)
    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')
