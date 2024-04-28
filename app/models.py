from app import db


class Bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.String(64), nullable=False)
    departure_date = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    booking_date = db.Column(db.String(64), nullable=False)


class Details(db.Model):
    __tablename__ = 'details'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    admin_comment = db.Column(db.String(65536), default='')


class Passports(db.Model):
    __tablename__ = 'passports'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    passport_number = db.Column(db.Integer, nullable=False)
    fio = db.Column(db.String(1024), nullable=True)
    granted = db.Column(db.String(256), nullable=True)
    granted_date = db.Column(db.String(64), nullable=True)
    department_code = db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(64), nullable=True)
    birth_date = db.Column(db.String(64), nullable=True)
    birthplace = db.Column(db.String(256), nullable=True)
    series = db.Column(db.Integer, nullable=True)
    number = db.Column(db.Integer, nullable=True)


class BlockedDate(db.Model):
    __tablename__ = 'blocked_date'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), nullable=False)
