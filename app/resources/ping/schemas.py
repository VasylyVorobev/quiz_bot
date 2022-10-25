from marshmallow import Schema
from marshmallow.fields import Str


class PingSchema(Schema):
    ping = Str()
