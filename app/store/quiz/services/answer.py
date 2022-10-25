import typing

from sqlalchemy import insert

from resources.quiz.models import answers
from resources.quiz.schemas import AnswerCreateSchema

if typing.TYPE_CHECKING:
    from web.app import Application


class AnswerService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_answers(self, answers_data: list[AnswerCreateSchema]):
        query = (
            insert(answers)
            .values([answer for answer in answers_data])
            .returning(
                answers.c.id,
                answers.c.title,
                answers.c.is_correct,
                answers.c.question,
            )
        )
        async with self.app.database.engine.connect() as conn:
            res = (await conn.execute(query)).fetchall()
            await conn.commit()
            return res
