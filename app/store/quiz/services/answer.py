import typing

from sqlalchemy import insert, func, select
from sqlalchemy.ext.asyncio import AsyncConnection

from resources.quiz.models import answers
from resources.quiz.schemas import AnswerCreateSchema
from resources.quiz.typing import AnswersList

if typing.TYPE_CHECKING:
    from web.app import Application


class AnswerService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_answers(
        self,
        answers_data: list[AnswerCreateSchema],
        question: int,
        conn: None | AsyncConnection = None
    ) -> tuple[int, str, bool, int]:

        query = (
            insert(answers)
            .values([
                {
                    "title": answer.title,
                    "is_correct": answer.is_correct,
                    "question": answer.question or question
                } for answer in answers_data
            ])
            .returning(
                answers.c.id,
                answers.c.title,
                answers.c.is_correct,
                answers.c.question,
            )
        )
        if conn:
            return (await conn.execute(query)).fetchall()
        async with self.app.store.db.engine.connect() as conn:
            res = (await conn.execute(query)).fetchall()
            await conn.commit()
            return res

    async def get_answers(self, questions_id: typing.Iterable[int]) -> AnswersList:
        query = select(answers).where(answers.c.question.in_(questions_id))
        async with self.app.store.db.engine.connect() as conn:
            res = await conn.execute(query)
            return AnswersList(**{
                "count": await self.get_answers_count(),
                "result": res.fetchall()
            })

    async def get_answers_count(self) -> int:
        query = select(func.count()).select_from(answers)
        async with self.app.store.db.engine.connect() as conn:
            return (await conn.execute(query)).scalar()
