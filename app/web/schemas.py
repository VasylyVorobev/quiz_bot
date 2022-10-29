from dataclasses import field

from marshmallow.validate import OneOf
from marshmallow_dataclass import dataclass


@dataclass
class BaseResponseSchema:
    status: str = field(metadata={"validate": OneOf(["ok", "error"])})
    data: dict
