import asyncio
import typing
from dataclasses import asdict
from json import dumps
from logging import getLogger
from uuid import uuid4

from aiohttp import ClientSession

from store.base.accessor import BaseAccessor
from store.clients.tg.api import TgClient
from store.tg.dcs import UpdateObj, ReplyKeyboardMarkup, KeyBoardButton

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
        if update.message.text.startswith("/start"):
            created, user = await self.app.store.user.get_or_create_user(
                tg_id=update.message.from_.id,
                username=update.message.from_.username
            )
            buttons = [[KeyBoardButton(text=str(uuid4())) for i in range(2)] for i in range(3)]
            keyboard = asdict(ReplyKeyboardMarkup(keyboard=buttons))
            data = await self.tg_client.send_message(
                update.message.chat.id,
                update.message.text,
                reply_markup=keyboard
            )
        else:
            data = await self.tg_client.send_message(update.message.chat.id, update.message.text)
        self.logger.info("send message %s", data)
