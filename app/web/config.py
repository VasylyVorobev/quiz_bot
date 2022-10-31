import typing
from dataclasses import dataclass
from os import environ

from yarl import URL

if typing.TYPE_CHECKING:
    from web.app import Application


@dataclass(slots=True)
class DbConfig:
    POSTGRES_USER: str
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_SCHEMA: str = "postgresql+asyncpg"

    @property
    def db_url(self) -> str:
        return str(
            URL.build(
                scheme=self.POSTGRES_SCHEMA,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=int(self.POSTGRES_PORT)
            ) / self.POSTGRES_DB
        )


@dataclass(slots=True)
class RabbitConfig:
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    @property
    def rabbit_url(self) -> str:
        return str(URL.build(
            scheme="amqp",
            user=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD,
            host=self.RABBITMQ_HOST,
            port=int(self.RABBITMQ_PORT)
        ))


@dataclass(slots=True)
class TgConfig:
    BOT_TOKEN: str


@dataclass(slots=True)
class AdminConfig:
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    SESSION_KEY: str


@dataclass(slots=True)
class Config:
    db: DbConfig
    rabbit: RabbitConfig
    admin_info: AdminConfig
    tg: TgConfig


def get_config() -> Config:
    return Config(
        db=DbConfig(
            POSTGRES_USER=environ.get("POSTGRES_USER"),
            POSTGRES_HOST=environ.get("POSTGRES_HOST"),
            POSTGRES_PASSWORD=environ.get("POSTGRES_PASSWORD"),
            POSTGRES_PORT=environ.get("POSTGRES_PORT"),
            POSTGRES_DB=environ.get("POSTGRES_DB")
        ),
        rabbit=RabbitConfig(
            RABBITMQ_HOST=environ.get("RABBITMQ_HOST"),
            RABBITMQ_PORT=environ.get("RABBITMQ_PORT"),
            RABBITMQ_USER=environ.get("RABBITMQ_USER"),
            RABBITMQ_PASSWORD=environ.get("RABBITMQ_PASSWORD")
        ),
        admin_info=AdminConfig(
            ADMIN_EMAIL=environ.get("ADMIN_EMAIL"),
            ADMIN_PASSWORD=environ.get("ADMIN_PASSWORD"),
            SESSION_KEY=environ.get("SESSION_KEY")
        ),
        tg=TgConfig(
            BOT_TOKEN=environ.get("BOT_TOKEN")
        )
    )


def setup_config(app: "Application") -> None:
    app.config = get_config()
