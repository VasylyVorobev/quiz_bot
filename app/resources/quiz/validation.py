from typing import TYPE_CHECKING

from marshmallow import ValidationError

if TYPE_CHECKING:
    from resources.quiz.schemas import AnswerCreateSchema


def validate_answers(answers: list["AnswerCreateSchema"]) -> None:
    if len(answers) < 2:
        raise ValidationError("There should be at least 2 answers.")

    if len(list(filter(lambda x: x.is_correct, answers))) != 1:
        raise ValidationError("There should be only one correct answer.")
