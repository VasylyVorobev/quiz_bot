import logging

import pytest
from aiohttp.test_utils import TestClient, loop_context
from aiohttp_apispec import setup_aiohttp_apispec
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from store import Database, setup_store, Store
from store.database import metadata
from web.app import Application
from web.config import setup_config, Config
from web.middlewares import setup_middlewares
from web.routes import setup_routes
from .fixtures import *  # noqa


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

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    return app


@pytest.fixture(autouse=True, scope="function")
async def clear_db(server):
    yield

    try:
        session = AsyncSession(server.database.engine)
        connection = session.connection()
        for table in metadata.tables:
            await session.execute(text(f"TRUNCATE {table} CASCADE"))
            await session.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"))

        await session.commit()
        connection.close()

    except (Exception, ) as err:
        logging.warning(err)


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture
def db_session(server):
    return server.database.engine


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))
