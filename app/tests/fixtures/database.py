import os
from uuid import uuid4

import pytest
from alembic import command
from sqlalchemy import text
from sqlalchemy_utils import create_database, drop_database
from alembic.config import Config as AlembicConfig

from store.database import metadata
from web.config import Config, get_config


@pytest.fixture(scope="session")
def temp_db_config() -> Config:
    config = get_config()
    test_db_name = f"{config.db.POSTGRES_DB}_{uuid4()}"
    config.db.POSTGRES_DB = test_db_name
    config.db.POSTGRES_SCHEMA = "postgresql"
    os.environ["POSTGRES_DB"] = test_db_name
    return config


@pytest.fixture(scope="session")
def temp_db_create(temp_db_config: Config):
    pg_url = temp_db_config.db.db_url
    create_database(pg_url)
    yield
    drop_database(pg_url)


@pytest.fixture(scope="session")
def alembic_cfg(temp_db_config: Config) -> AlembicConfig:
    return AlembicConfig('alembic.ini')


@pytest.fixture(scope='session', autouse=True)
def db_migrated(temp_db_create: None, alembic_cfg: AlembicConfig) -> None:
    command.upgrade(alembic_cfg, 'head')


@pytest.fixture(autouse=True, scope="function")
async def db(store):
    yield

    async with store.db.engine.begin() as session:
        for table in metadata.tables:
            await session.execute(text(f'TRUNCATE {table} CASCADE'))


@pytest.fixture
def db_session(store):
    return store.db.engine
