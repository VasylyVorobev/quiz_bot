from logging import getLogger
from typing import TYPE_CHECKING
from store.base.abstract import AbstractAccessor

if TYPE_CHECKING:
    from web.app import Application


class BaseAccessor(AbstractAccessor):

    def __init__(self, app: "Application", *_, **__):
        self.app = app
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_shutdown.append(self.disconnect)

    async def connect(self, app: "Application"):
        return

    async def disconnect(self, app: "Application"):
        return
