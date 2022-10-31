from sqlalchemy import select, exists, or_, insert

from store.base.accessor import BaseAccessor
from resources.user.models import users


class UserAccessor(BaseAccessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    async def create_user(self, tg_id: int, username: str) -> None | tuple[int, str, bool]:
        if await self.is_user_exists(tg_id, username):
            return

        query = (
            insert(users)
            .values(id=tg_id, username=username)
            .returning(
                users.c.id,
                users.c.username,
                users.c.is_admin,
            )
        )
        async with self.app.store.db.engine.connect() as conn:
            res = (await conn.execute(query)).fetchone()
            await conn.commit()
            return res

    async def get_user(self, tg_id: int) -> tuple[int, str, bool]:
        query = select(users).where(users.c.id == tg_id)
        async with self.app.store.db.engine.connect() as conn:
            res = await conn.execute(query)
            return res.fetchone()

    async def get_or_create_user(
            self,
            tg_id: int,
            username: str
    ) -> tuple[bool, tuple[int, str, bool]]:
        if user := await self.create_user(tg_id, username):
            return True, user
        return False, await self.get_user(tg_id)
