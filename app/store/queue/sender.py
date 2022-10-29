from typing import TYPE_CHECKING

from aio_pika import Message
from aio_pika.abc import AbstractConnection


if TYPE_CHECKING:
    from web.app import Application


class SenderQueue:
    def __init__(self, app: "Application", connection: None | AbstractConnection):
        self._connection = connection
        self.app = app
        self.queue_name = "telegram_queue"

    async def send_message(self, message: str) -> None:
        channel = await self._connection.channel()
        await channel.declare_queue(self.queue_name)
        await channel.set_qos(prefetch_count=100)
        await channel.default_exchange.publish(
            Message(message.encode()),
            routing_key=self.queue_name
        )
