import asyncio
from typing import TYPE_CHECKING, Callable, Awaitable
from logging import getLogger

from aiohttp import ClientSession

from store.base.accessor import BaseAccessor
from store.clients.tg.api import TgClient
from store.tg.constants import EntityType
from store.tg.dcs import UpdateObj, Message, CallbackQuery

if TYPE_CHECKING:
    from web.app import Application

CommandHandlerCallable = Callable[[Message], Awaitable[None]]
QueryHandlerCallable = Callable[[CallbackQuery], Awaitable[None]]


class TgAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.logger = getLogger(__name__)
        self.session: None | ClientSession = None
        self.token = self.app.config.tg.BOT_TOKEN
        self.tg_client: None | TgClient = None
        self.task: None | asyncio.Task = None
        self.commands: dict[str, CommandHandlerCallable] = {}
        self.query_handler: dict[str, QueryHandlerCallable] = {}

    def register_command_handler(
            self, command: str, func: CommandHandlerCallable
    ) -> None:
        self.commands[command] = func

    def register_query_handler(
            self, command: str, function
    ) -> None:
        self.query_handler[command] = function

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
            updates = await self.tg_client.get_updates_in_objects(offset=offset, timeout=60)
            for update in updates.result:
                offset = update.update_id + 1
                await self._handle_update(update)

    async def _handle_update(self, update: UpdateObj) -> None:
        if message := update.message:
            await self._handle_message(message)
        elif callback_query := update.callback_query:
            await self._handle_callback_query(callback_query)

    async def _handle_message(self, message: Message) -> None:
        if not message.text or not message.entities:
            return

        entity = message.entities[0]
        if entity.type is EntityType.bot_command:
            command = message.text[entity.offset:entity.offset + entity.length]
            command_without_mention = command.split("@")[0]
            if handler := self.commands.get(command_without_mention):
                await handler(message)

    async def _handle_callback_query(self, callback_query: CallbackQuery) -> None:
        if not callback_query.data:
            self.logger.warning("cannot handle callback_query: %s", callback_query)
            return

        prefix, data = callback_query.data.split(maxsplit=1)
        if query_handler := self.query_handler.get(prefix):
            callback_query.data = data
            await query_handler(callback_query)
        else:
            self.logger.error("Query handler not found: %s", callback_query)
            await self.app.store.tg.tg_client.answer_callback_query(
                callback_query_id=data.id
            )
