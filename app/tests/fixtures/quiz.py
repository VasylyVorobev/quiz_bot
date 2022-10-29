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


@pytest.fixture
async def create_quizzes(cli, db_session, get_programming_language):
    language_id, _ = get_programming_language
    res = []
    for i in range(3):
        data = {
            "language_id": language_id,
            "title": f"Question {i} ?",
            "answers": [
                {
                    "title": "Answer 1",
                    "is_correct": True
                },
                {
                    "title": "Answer 2",
                    "is_correct": False
                }
            ]
        }
        resp = await cli.post("/api/v1/quiz/", json=data)
        res.append(await resp.json())

    return res
