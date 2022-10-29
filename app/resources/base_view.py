from typing import TYPE_CHECKING

from aiohttp.web import View as AiohttpView


if TYPE_CHECKING:
    from store import Store
    from web.app import Request


class View(AiohttpView):
    @property
    def request(self) -> "Request":
        return super().request

    @property
    def store(self) -> "Store":
        return self.request.app.store

    @property
    def data(self):
        return self.request.get("data", {})
