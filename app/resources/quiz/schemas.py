from dataclasses import fields, field
from itertools import groupby
from typing import get_type_hints, ClassVar, Type, Optional

from marshmallow import Schema, post_load
from marshmallow.fields import Str, Int
from marshmallow.validate import Range
from marshmallow_dataclass import dataclass

from resources.quiz.typing import GetProgrammingLanguages, QuizCreateResponse, QuizListResponse
from resources.quiz.validation import validate_answers
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
    question: Optional[int] = field(default=None, metadata={"dump_only": True})
    id: Optional[int] = field(default=None, metadata={"dump_only": True})

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass(order=True)
class QuizCreateSchema:
    title: str
    language_id: int
    answers: list[AnswerCreateSchema] = field(metadata={"validate": validate_answers})
    id: Optional[int] = field(default=None, metadata={"dump_only": True})

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class QuizDetailResponseSchema(BaseResponseSchema):
    data: QuizCreateSchema

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class QuizListResponseSchema(BaseResponseSchema):
    data: list[QuizCreateSchema]

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass(order=True)
class QuizListSchema:
    count: int
    result: list[QuizCreateSchema]

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class QuestionDetailSchema:
    id: int
    title: str
    language: int


@dataclass
class QuestionListSchema:
    count: int
    result: list[QuestionDetailSchema]


@schema_converter.register
def convert_create_programming_language_to_schema(
        data: tuple[int, str]
) -> ProgrammingLanguageCreateResponseSchema:
    schema_fields = [
        f.name for f in fields(ProgrammingLanguageCreateResponseSchema)
    ]
    result = dict(zip(schema_fields, data))
    return ProgrammingLanguageCreateResponseSchema.Schema().load(result)


@schema_converter.register
def convert_list_programming_language_to_schema(
        data: GetProgrammingLanguages
) -> ProgrammingLanguageListSchema:
    type_hints = get_type_hints(ProgrammingLanguageListSchema)
    schema_fields = [f.name for f in fields(type_hints["result"].__args__[0])]
    result = {
        "count": data.count,
        "result": [dict(zip(schema_fields, obj)) for obj in data.result]
    }
    return ProgrammingLanguageListSchema.Schema().load(result)


@schema_converter.register
def convert_question_detail_to_schema(quiz_data: QuizCreateResponse) -> QuizCreateSchema:
    question_id, title, language = quiz_data.question
    res = QuizCreateSchema(
        id=question_id,
        language_id=language,
        title=title,
        answers=[
            AnswerCreateSchema(
                id=answer_id,
                title=title,
                is_correct=is_correct,
                question=question
            ) for answer_id, title, is_correct, question in quiz_data.answers
        ]
    )
    return res


@schema_converter.register
def convert_quizzes_to_schema(data: QuizListResponse) -> QuizListSchema:
    result = []
    for key, value in groupby(data.answers, lambda x: x[3]):
        _, title, language = next(i for i in data.questions.result if i[0] == key)
        result.append(
            QuizCreateSchema(
                id=key,
                title=title,
                language_id=language,
                answers=[
                    AnswerCreateSchema(
                        id=answer_id,
                        title=title,
                        is_correct=is_correct,
                        question=question
                    ) for answer_id, an_title, is_correct, question in value
                ]
            )
        )

    return QuizListSchema(
        count=data.questions.count,
        result=result
    )
