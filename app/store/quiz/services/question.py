import typing

from sqlalchemy import insert

from resources.quiz.models import questions

if typing.TYPE_CHECKING:
    from web.app import Application


class QuestionService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_question(self, language_id: int, title: str):
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
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            data = res.fetchone()
            await conn.commit()
            return data
