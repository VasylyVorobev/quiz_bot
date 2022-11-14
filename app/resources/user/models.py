from sqlalchemy import Table, Column, Integer, VARCHAR, Boolean, false, ForeignKey

from store.database.metadata import metadata


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),  # telegram id
    Column("username", VARCHAR(100), nullable=False),
    Column("is_admin", Boolean, server_default=false(), nullable=False),

    Column("current_language", Integer, ForeignKey("programming_languages.id")),
)
