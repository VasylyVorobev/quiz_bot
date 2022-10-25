from dataclasses import is_dataclass, asdict
from functools import wraps
from typing import Callable, Union, Type, get_type_hints

from marshmallow import Schema

from utils.custom_response import json_response

RawSqlConverterFunction = Callable[[Union[tuple, list[tuple]]], Type[Schema]]


class ConvertToSchema:
    def __init__(self):
        self.converters: dict[Type[Schema], RawSqlConverterFunction] = {}

    @staticmethod
    def _is_schemed_dataclass(cls) -> bool:
        return is_dataclass(cls) and hasattr(cls, "Schema")

    def register(self, wrapped: RawSqlConverterFunction) -> RawSqlConverterFunction:
        type_hints = get_type_hints(wrapped)
        return_type = type_hints.pop("return")
        assert self._is_schemed_dataclass(return_type), "Bad return type"

        self.converters[return_type] = wrapped

        return wrapped

    def convert_to_schema(self, schema: Type[Schema]):

        def _decorator(wrapped):
            @wraps(wrapped)
            async def inner(handler):
                status = 200
                result = await wrapped(handler)
                if isinstance(result, tuple):
                    result, status = result

                data = self.converters[schema](result)
                return json_response(data=asdict(data), http_status=status)

            return inner

        return _decorator


schema_converter = ConvertToSchema()
