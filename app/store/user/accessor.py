from sqlalchemy import select, exists, or_, insert, update, and_

from store.base.accessor import BaseAccessor
from resources.user.models import users
from resources.quiz.models import questions_users


class UserAccessor(BaseAccessor):

    async def is_user_exists(self, tg_id: int, username: str) -> bool:
        query = (
            select(
                [exists().where(
                    or_(
                        users.c.id == tg_id,
                        users.c.username == username
                    )
                )]
            )
        )
        async with self.app.store.db.engine.connect() as conn:
            res = await conn.execute(query)
            return res.scalar()

    async def create_user(self, tg_id: int, username: str) -> None | tuple[int, str, bool, int]:
        if await self.is_user_exists(tg_id, username):
            return

        query = (
            insert(users)
            .values(id=tg_id, username=username)
            .returning(
                users.c.id,
                users.c.username,
                users.c.is_admin,
                users.c.current_language
            )
        )
        async with self.app.store.db.engine.connect() as conn:
            res = (await conn.execute(query)).fetchone()
            await conn.commit()
            return res

    async def get_user(self, tg_id: int) -> tuple[int, str, bool, int]:
        query = select(users).where(users.c.id == tg_id)
        async with self.app.store.db.engine.connect() as conn:
            res = await conn.execute(query)
            return res.fetchone()

    async def get_or_create_user(
            self,
            tg_id: int,
            username: str
    ) -> tuple[bool, tuple[int, str, bool, int]]:
        if user := await self.create_user(tg_id, username):
            return True, user
        return False, await self.get_user(tg_id)

    async def change_user_language(self, user_id: int, language_id: int) -> None:
        query = (
            update(users)
            .where(users.c.id == user_id)
            .values(current_language=language_id)
        )
        async with self.app.store.db.engine.connect() as conn:
            await conn.execute(query)
            await conn.commit()

    async def is_question_user_exists(self, user_id: int, question_id: int) -> bool:
        query = (
            select([
                exists().where(
                    and_(
                        questions_users.c.user == user_id,
                        questions_users.c.question == question_id
                    )
                )
            ])
        )
        async with self.app.store.db.engine.connect() as conn:
            res = await conn.execute(query)
            return res.scalar()

    async def set_question_status_to_user(
            self, question_id: int, user_id: int, is_correct: bool
    ) -> None:
        if await self.is_question_user_exists(user_id, question_id):
            query = (
                update(questions_users)
                .where(
                    and_(
                        questions_users.c.user == user_id,
                        questions_users.c.question == question_id
                    )
                )
                .values(is_correct=is_correct)
            )
        else:
            query = (
                insert(questions_users)
                .values(
                    is_correct=is_correct,
                    user=user_id,
                    question=question_id,
                )
            )
        async with self.app.store.db.engine.connect() as conn:
            await conn.execute(query)
            await conn.commit()
