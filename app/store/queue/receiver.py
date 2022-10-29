from logging import getLogger
from typing import TYPE_CHECKING
from json import loads

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractConnection, AbstractIncomingMessage

from store.tg.dcs import UpdateObj

if TYPE_CHECKING:
    from web.app import Application


class MessageReceiver:
    def __init__(self, app: "Application", connection: AbstractConnection):
        self._connection = connection
        self.queue_name = "telegram_queue"
        self.app = app
        self.logger = getLogger(__name__)

    async def handle_queue_message(self):
        channel = await self._connection.channel()
        queue = await channel.declare_queue(self.queue_name)
        await queue.consume(self.on_message)

    async def on_message(self, message: IncomingMessage | AbstractIncomingMessage):
        async with message.process():
            self.logger.info("Get new message %s", message.body)
            response: UpdateObj = UpdateObj.Schema().load(loads(message.body))
            await self.app.store.tg.handle_update(response)
