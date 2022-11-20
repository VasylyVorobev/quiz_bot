from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

if TYPE_CHECKING:
    from web.app import Application


class Database:

    def __init__(self, app: "Application"):
        self.app = app
        self.engine: Optional[AsyncEngine] = None

    async def connect(self, *_, **__) -> None:
        self.engine: AsyncEngine = create_async_engine(
            self.app.config.db.db_url,
            # echo=True,
            future=True
        )

    async def disconnect(self, *_, **__) -> None:
        if self.engine:
            await self.engine.dispose()
