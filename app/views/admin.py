from flask import render_template, request, redirect, session, url_for, Response, Blueprint
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from app import db, login_manager
from app.models import Bookings, Details, Passports, BlockedDate

from app.utils import get_current_date, format_date

from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import UnmappedInstanceError, NoResultFound

from datetime import timedelta, datetime
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
        if username == "riba-kit" and password == "riba-admin":
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

        if field_key == "entry_date":
            start_date = field_value
            end_date = booking.departure_date
        else:
            start_date = booking.departure_date
            end_date = field_value

        if can_change_booking(booking.id, start_date, end_date):
            setattr(booking, field_key, field_value)
        else:
            response = {"status": 400}
            return Response(response=json.dumps(response, ensure_ascii=False), status=400, mimetype='application/json')
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


@admins.route("/admin/date/block", methods=['POST'])
def block_dates():
    start_date = datetime.strptime(request.json["firstDate"], "%d.%m.%Y")
    end_date = datetime.strptime(request.json["secondDate"], "%d.%m.%Y")

    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]

    current_date = datetime.strptime(get_current_date(return_time=False), '%d.%m.%Y')
    filtered_dates = [date.strftime('%d.%m.%Y') for date in date_range if date >= current_date]

    for date in filtered_dates:
        try:
            new_blocked_date = BlockedDate(date=date)
            db.session.add(new_blocked_date)
        except UnmappedInstanceError:
            pass

    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


@admins.route("/admin/date/unlock", methods=['POST'])
def unlock_dates():
    start_date = datetime.strptime(request.json["firstDate"], "%d.%m.%Y")
    end_date = datetime.strptime(request.json["secondDate"], "%d.%m.%Y")

    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    date_range = [date.strftime('%d.%m.%Y') for date in date_range]

    for date in date_range:
        try:
            blocked_date = BlockedDate.query.filter_by(date=date).first()
            db.session.delete(blocked_date)
        except UnmappedInstanceError:
            pass

    db.session.commit()

    response = {"status": 200}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')


def can_change_booking(booking_id, new_entry_date_str, new_departure_date_str):
    new_entry_date = datetime.strptime(str(new_entry_date_str), '%d.%m.%Y')
    new_departure_date = datetime.strptime(str(new_departure_date_str), '%d.%m.%Y')

    overlapping_bookings = Bookings.query.filter(and_(
        Bookings.id != booking_id, or_(Bookings.status == 'confirmed', Bookings.status == 'pending')
    )
    ).all()

    current_date = new_entry_date
    while current_date < new_departure_date:
        bookings_count = 0
        for booking in overlapping_bookings:
            booking_entry_date = datetime.strptime(booking.entry_date, '%d.%m.%Y')
            booking_departure_date = datetime.strptime(booking.departure_date, '%d.%m.%Y')

            if booking_entry_date <= current_date < booking_departure_date:
                bookings_count += 1

        if bookings_count >= 2:
            return False
        current_date += timedelta(days=1)

    departure_day_bookings = 0
    for booking in overlapping_bookings:
        booking_entry_date = datetime.strptime(booking.entry_date, '%d.%m.%Y')
        booking_departure_date = datetime.strptime(booking.departure_date, '%d.%m.%Y')

        if booking_entry_date == current_date:
            departure_day_bookings += 1

    if departure_day_bookings >= 2:
        return False

    return True
