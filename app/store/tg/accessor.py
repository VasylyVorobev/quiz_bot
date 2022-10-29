import asyncio
import typing
from json import dumps
from logging import getLogger

from aiohttp import ClientSession

from store.base.accessor import BaseAccessor
from store.clients.tg.api import TgClient
from store.tg.dcs import UpdateObj

if typing.TYPE_CHECKING:
    from web.app import Application


class TgAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.logger = getLogger(__name__)
        self.session: None | ClientSession = None
        self.token = self.app.config.tg.BOT_TOKEN
        self.tg_client: None | TgClient = None
        self.task: None | asyncio.Task = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        self.tg_client = TgClient(self.token, self.session)
        self.task = asyncio.create_task(self._worker())

    async def disconnect(self, app: "Application"):

        if self.task:
            await self.task
            try:
                self.task.cancel()
            except asyncio.CancelledError:
                pass

        if self.session:
            await self.session.close()

    async def _worker(self):
        offset = 0
        while True:
            updates = await self.tg_client.get_updates(offset=offset, timeout=60)
            for update in updates["result"]:
                offset = update["update_id"] + 1
                await self.app.store.queue.sender.send_message(dumps(update))

    async def handle_update(self, update: UpdateObj):
        data = await self.tg_client.send_message(update.message.chat.id, update.message.text)
        self.logger.info("send message %s", data)
