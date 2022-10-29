import asyncio
from typing import TYPE_CHECKING

from aio_pika import connect
from aio_pika.abc import AbstractConnection

from store.base.accessor import BaseAccessor
from store.queue.receiver import MessageReceiver
from store.queue.sender import SenderQueue

if TYPE_CHECKING:
    from web.app import Application


class BaseQueue(BaseAccessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rabbit_url = self.app.config.rabbit.rabbit_url
        self._connection: None | AbstractConnection = None
        self.tasks_receiver: list[asyncio.Task] = []
        self.concurrent_workers = 10

        self.sender: None | SenderQueue = None
        self.receiver: None | MessageReceiver = None

    async def connect(self, app: "Application"):
        if not self._connection:
            self._connection = await connect(self.rabbit_url)

        self.receiver = MessageReceiver(app, self._connection)
        self.tasks_receiver = [
            asyncio.create_task(self.receiver.handle_queue_message())
            for _ in range(self.concurrent_workers)
        ]
        self.sender = SenderQueue(app, self._connection)

    async def disconnect(self, app: "Application") -> None:

        if self._connection:
            await self._connection.close()
            self._connection = None
        if self.tasks_receiver:
            tasks = await asyncio.gather(*self.tasks_receiver)
            for task in tasks:
                if task is not None:
                    try:
                        task: asyncio.Task
                        task.cancel()
                    except asyncio.CancelledError:
                        continue
