from flask import render_template, request, jsonify, Blueprint, Response

from app import db
from app.models import Bookings, Details, BlockedDate
from app.schemas import BookingSchema

from app.utils import get_current_date, format_date
from marshmallow import ValidationError

from app.utils import send_notification

from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import or_
import json

api = Blueprint('api', __name__)
static_pages = Blueprint('static_pages', __name__)


@api.route('/booking', methods=['POST'])
def booking():
    schema = BookingSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        print(err.messages)
        return jsonify(err.messages), 400

    print(data)

    date_now = get_current_date(timezone='Europe/Moscow')

    new_booking = Bookings(
        entry_date=data['firstDate'],
        departure_date=data['secondDate'],
        status="pending",
        booking_date=date_now
    )

    db.session.add(new_booking)
    db.session.commit()

    name = "{surname} {name} {patronymic}".format(
        surname=data['surname'], name=data['name'], patronymic=data['patronymic']
    )

    new_details = Details(
        booking_id=new_booking.id,
        name=name,
        adults=data['adults'],
        children=data['children'],
        phone=data['phone'],
        email=data['email']
    )

    db.session.add(new_details)
    db.session.commit()

    message = f"Новое бронирование от {date_now}"
    send_notification(message=message)

    return jsonify({'status': 200, 'message': 'Booking'})


@static_pages.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@static_pages.route('/free-dates', methods=['GET'])
def get_free_dates():
    bookings = Bookings.query.filter(
        or_(
            Bookings.status == "pending",
            Bookings.status == "confirmed"
        )
    ).all()

    date_ranges = []
    for current_booking in bookings:
        start_date = datetime.strptime(current_booking.entry_date, "%d.%m.%Y")
        end_date = datetime.strptime(current_booking.departure_date, "%d.%m.%Y")
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
        date_ranges.extend(date_range)

    date_counts = Counter(date_ranges)
    overlapping_dates = [date for date, count in date_counts.items() if count > 1]

    current_date = datetime.strptime(get_current_date(return_time=False), '%d.%m.%Y')
    filtered_dates = [format_date(date) for date in overlapping_dates if date >= current_date]

    blocked_dates = BlockedDate.query.all()
    filtered_blocked_dates = [format_date(date) for date in blocked_dates if date >= current_date]

    filtered_dates.extend(filtered_blocked_dates)

    response = {"status": 200, "dates": filtered_dates}
    return Response(response=json.dumps(response, ensure_ascii=False), status=200, mimetype='application/json')
