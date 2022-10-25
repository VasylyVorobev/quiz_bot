from sqlalchemy import Table, Column, Integer, VARCHAR, ForeignKey, Boolean, false

from store.database.metadata import metadata


programming_languages = Table(
    "programming_languages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", VARCHAR(50), unique=True, nullable=False)
)


questions = Table(
    "questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", VARCHAR(50), unique=True, nullable=False),

    Column("language", Integer, ForeignKey("programming_languages.id"), nullable=False)
)


answers = Table(
    "answers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", VARCHAR(150), nullable=False),
    Column("is_correct", Boolean, nullable=False, server_default=false()),

    Column("question", Integer, ForeignKey("questions.id"), nullable=False)
)


questions_users = Table(
    "questions_users",
    metadata,
    Column("id", Integer, primary_key=True),

    Column("user", Integer, ForeignKey("users.id"), nullable=False),
    Column("question", Integer, ForeignKey("questions.id"), nullable=False),
)
