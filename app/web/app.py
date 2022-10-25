from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec

from store import Store, setup_store
from store.database.database import Database
from web.config import Config, setup_config
from web.logger import setup_logging
from web.middlewares import setup_middlewares
from web.routes import setup_routes


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self):
        return self.request.get("data", {})


app = Application()


async def setup_app():
    setup_logging(app)
    setup_config(app)

    setup_routes(app)
    setup_aiohttp_apispec(
        app, title="Telegram Bot Quiz", url="/docs/json", swagger_path="/docs"
    )

    setup_middlewares(app)
    setup_store(app)
    return app
