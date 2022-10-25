import pytest

from resources.quiz.models import programming_languages


@pytest.fixture
async def get_programming_languages(db_session):
    query = programming_languages.insert(values=[
        {"title": "python"},
        {"title": "sql"},
        {"title": "java"},
        {"title": "golang"},
        {"title": "scala"},
    ]).returning(*programming_languages.columns)
    async with db_session.connect() as conn:
        res = await conn.execute(query)
        data = res.fetchall()
        await conn.commit()
        return data


@pytest.fixture
async def get_programming_language(db_session):
    query = (
        programming_languages
        .insert(values={"title": "javascript"})
        .returning(*programming_languages.columns)
    )
    async with db_session.connect() as conn:
        res = await conn.execute(query)
        data = res.fetchone()
        await conn.commit()
        return data
