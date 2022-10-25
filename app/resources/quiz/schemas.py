from dataclasses import fields, field
from typing import get_type_hints, ClassVar, Type, Optional

from marshmallow import Schema, post_load
from marshmallow.fields import Str, Int
from marshmallow.validate import Range, Length
from marshmallow_dataclass import dataclass

from resources.quiz.typing import GetProgrammingLanguages
from utils.schemas_converting import schema_converter
from web.schemas import BaseResponseSchema


class ProgrammingLanguageCreateSchema(Schema):
    title = Str(required=True)


class PageSchema(Schema):
    page = Int(validate=Range(min=1), load_default=1)
    page_size = Int(validate=Range(max=250), load_default=10)

    @post_load
    def convert_page(self, data: dict, **_) -> dict[str, int]:
        return {
            "limit": data["page_size"],
            "offset": (data["page"] - 1) * data["page_size"],
        }


@dataclass(order=True)
class ProgrammingLanguageCreateResponseSchema:
    id: int
    title: str

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class ProgrammingLanguageMatchInfoSchema:
    id: int

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass(order=True)
class ProgrammingLanguageListSchema:
    count: int
    result: list[ProgrammingLanguageCreateResponseSchema]

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class ProgrammingLanguageListResponseSchema(BaseResponseSchema):
    data: ProgrammingLanguageListSchema

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass(order=True)
class AnswerCreateSchema:
    is_correct: bool
    title: str
    question_id: Optional[int] = None

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass(order=True)
class QuestionCreateSchema:
    title: str
    language_id: int
    answers: list[AnswerCreateSchema] = field(metadata={"validate": Length(min=2)})

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class QuestionDetailResponseSchema(BaseResponseSchema):
    data: QuestionCreateSchema

    Schema: ClassVar[Type[Schema]] = Schema


@schema_converter.register
def convert_create_programming_language_to_schema(
        data: tuple[int, str]
) -> ProgrammingLanguageCreateResponseSchema:
    schema_fields = [
        field.name for field in fields(ProgrammingLanguageCreateResponseSchema)
    ]
    result = dict(zip(schema_fields, data))
    return ProgrammingLanguageCreateResponseSchema.Schema().load(result)


@schema_converter.register
def convert_list_programming_language_to_schema(
        data: GetProgrammingLanguages
) -> ProgrammingLanguageListSchema:
    type_hints = get_type_hints(ProgrammingLanguageListSchema)
    schema_fields = [field.name for field in fields(type_hints["result"].__args__[0])]
    result = {
        "count": data["count"],
        "result": [dict(zip(schema_fields, obj)) for obj in data["result"]]
    }
    return ProgrammingLanguageListSchema.Schema().load(result)


@schema_converter.register
def convert_question_detail_to_schema(
        data
) -> QuestionCreateSchema:
    pass
