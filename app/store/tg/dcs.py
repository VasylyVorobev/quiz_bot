from __future__ import annotations
from dataclasses import field
from typing import Optional, Type, ClassVar

from marshmallow import EXCLUDE, Schema  # noqa: F401
from marshmallow_dataclass import dataclass

from store.tg.constants import EntityType


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: str
    username: str
    language_code: Optional[str] = None
    last_name: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Entity:
    offset: int
    length: int
    type: EntityType

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    date: Optional[int] = None
    text: Optional[str] = None
    entities: Optional[list[Entity]] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class CallbackQuery:
    id: str
    data: str
    chat_instance: str
    from_: MessageFrom = field(metadata={"data_key": "from"})
    message: Optional[Message] = None


@dataclass
class UpdateObj:
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None

    Schema: ClassVar[Type[Schema]] = Schema  # noqa: F811

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: list[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema  # noqa: F811

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema  # noqa: F811

    class Meta:
        unknown = EXCLUDE


@dataclass
class InlineKeyboardButton:
    text: str
    callback_data: str

    Schema: ClassVar[Type[Schema]] = Schema  # noqa: F811


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]]

    Schema: ClassVar[Type[Schema]] = Schema  # noqa: F811
