from marshmallow_dataclass import dataclass


@dataclass
class BaseResponseSchema:
    status: str
    data: dict
