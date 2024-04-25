from marshmallow import Schema, fields


class BookingSchema(Schema):
    firstDate = fields.Str(required=True)
    secondDate = fields.Str(required=True)
    adults = fields.Int(required=True)
    children = fields.Int(required=True)
    surname = fields.Str(required=True)
    name = fields.Str(required=True)
    patronymic = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Email(required=True)
