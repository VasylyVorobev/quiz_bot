from dataclasses import field
from typing import Optional, Type, ClassVar

from marshmallow import EXCLUDE, Schema  # noqa: F401
from marshmallow_dataclass import dataclass


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
class Message:
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    date: Optional[int] = None
    text: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Message

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
