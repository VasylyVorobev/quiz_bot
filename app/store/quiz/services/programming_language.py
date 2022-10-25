import typing

from aiohttp.web_exceptions import HTTPBadRequest
from sqlalchemy import select, exists, func, update, and_, insert

from resources.quiz.models import programming_languages
from resources.quiz.typing import GetProgrammingLanguages

if typing.TYPE_CHECKING:
    from web.app import Application


class ProgrammingLanguageService:
    def __init__(self, app: "Application"):
        self.app = app

    async def create_programming_language(self, title: str) -> None | tuple[int, str]:
        if await self.is_programming_language_exists(title):
            return
        query = (
            insert(programming_languages)
            .values(title=title)
            .returning(*programming_languages.columns)
        )
        async with self.app.database.engine.connect() as conn:
            res = (await conn.execute(query)).fetchone()
            await conn.commit()
            return res

    async def is_programming_language_exists(self, title: str) -> bool:
        query = select([exists().where(programming_languages.c.title == title)])
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return res.scalar()

    async def is_programming_language_exists_for_update(self, language_id: int, title: str) -> bool:
        exists_query = (
            exists()
            .where(
                and_(
                    programming_languages.c.title == title,
                    programming_languages.c.id != language_id
                )
            )
        )
        query = (
            select([exists_query])
        )
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return res.scalar()

    async def get_programming_languages(
            self,
            limit: int,
            offset: int
    ) -> GetProgrammingLanguages:
        query = select(programming_languages).limit(limit).offset(offset)
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return {
                "count": await self.get_programming_languages_count(),
                "result": res.fetchall()
            }

    async def get_programming_languages_count(self) -> int:
        query = select(func.count()).select_from(programming_languages)
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return res.scalar()

    async def get_programming_language(self, language_id: int) -> None | tuple[int, str]:
        query = select(programming_languages).where(programming_languages.c.id == language_id)
        async with self.app.database.engine.connect() as conn:
            res = await conn.execute(query)
            return res.one_or_none()

    async def update_programming_language(
            self,
            language_id: int,
            title: str
    ) -> None | tuple[int, str]:
        if await self.is_programming_language_exists_for_update(language_id, title):
            raise HTTPBadRequest(text="Such a programming language already exists")
        query = (
            update(programming_languages)
            .where(programming_languages.c.id == language_id)
            .values(title=title)
            .returning(*programming_languages.columns)
        )
        async with self.app.database.engine.connect() as conn:
            res = (await conn.execute(query)).fetchone()
            await conn.commit()
            return res
