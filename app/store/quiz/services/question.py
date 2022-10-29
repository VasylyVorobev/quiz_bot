import typing

from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncConnection

from resources.quiz.models import questions
from resources.quiz.typing import QuestionsList

if typing.TYPE_CHECKING:
    from web.app import Application


class QuestionService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_question(
            self,
            language_id: int,
            title: str,
            conn: None | AsyncConnection = None
    ) -> tuple[int, str, int]:
        query = (
            insert(questions)
            .values({
                "language": language_id,
                "title": title
            })
            .returning(
                questions.c.id,
                questions.c.title,
                questions.c.language
            )
        )
        if conn:
            return (await conn.execute(query)).fetchone()
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            data = res.fetchone()
            await conn.commit()
            return data

    async def get_questions(self, limit: int, offset: int) -> QuestionsList:
        query = select(questions).limit(limit).offset(offset)
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return QuestionsList(**{
                "count": await self.get_questions_count(),
                "result": res.fetchall()
            })

    async def get_questions_count(self) -> int:
        query = select(func.count()).select_from(questions)
        async with self.app.database.engine.connect() as conn:
            return (await conn.execute(query)).scalar()
