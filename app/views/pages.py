from flask import render_template, request, jsonify, Blueprint

from app import db
from app.models import Bookings, Details
from app.schemas import BookingSchema

from app.utils import get_current_time
from marshmallow import ValidationError

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

    date_now = get_current_time(timezone='Europe/Moscow')

    new_booking = Bookings(
        entry_date=data['firstDate'],
        departure_date=data['secondDate'],
        status="Ожидает подтверждения",
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

    return jsonify({'status': 200, 'message': 'Booking'})


@static_pages.route('/', methods=['GET'])
def main():
    return render_template('index.html')
