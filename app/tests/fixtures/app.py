import pytest
from aiohttp.test_utils import TestClient, loop_context
from aiohttp_apispec import setup_aiohttp_apispec

from store import setup_store, Store
from web.app import Application
from web.config import setup_config, Config
from web.middlewares import setup_middlewares
from web.routes import setup_routes


@pytest.fixture(scope="session")
def event_loop_():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture
def server():
    app = Application()
    setup_config(app)
    setup_routes(app)
    setup_aiohttp_apispec(
        app, title="Telegram Bot Quiz", url="/docs/json", swagger_path="/docs"
    )
    setup_middlewares(app)
    setup_store(app)

    app.on_startup.clear()
    app.on_shutdown.clear()

    app.on_startup.append(app.store.db.connect)
    app.on_shutdown.append(app.store.db.disconnect)

    return app


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))
