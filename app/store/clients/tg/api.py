from logging import getLogger
from typing import cast, Callable, Any
from functools import wraps

from aiohttp import ClientSession

from store.tg.dcs import GetUpdatesResponse, SendMessageResponse


logger = getLogger(__name__)


def _check_client_session(func: Callable[[str, str, None | dict], Any]):
    @wraps(func)
    def wrapped(*args, **kwargs):
        tg_client, *_ = args
        session = cast(ClientSession, tg_client.session)
        if not session or session.closed:
            logger.error("Session expired")
            tg_client.session = ClientSession()
        return func(*args, **kwargs)

    return wrapped


class TgClient:
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str, session: ClientSession):
        self.token = token
        self.session = session

    def get_url(self, method: str) -> str:
        return f"{self.BASE_URL}{self.token}/{method}"

    async def get_me(self) -> dict:
        return await self.make_request(
            http_method="get", method="getMe"
        )

    async def get_updates(self, offset: None | int = None, timeout: int = 0) -> dict:
        params = {}
        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout
        return await self.make_request(
            http_method="get", method="getUpdates", params=params
        )

    @_check_client_session
    async def make_request(
            self, http_method: str, method: str, params: None | dict = None
    ) -> dict:
        if http_method == "get":
            async with self.session.get(self.get_url(method), json=params or {}) as resp:
                return await resp.json()
        elif http_method == "post":
            async with self.session.post(self.get_url(method), json=params) as resp:
                return await resp.json()

        raise NotImplementedError

    async def get_updates_in_objects(
            self,
            offset: None | int = None,
            timeout: int = 0
    ) -> GetUpdatesResponse:
        updates = cast(dict, await self.get_updates(offset, timeout))
        return GetUpdatesResponse.Schema().load(updates)

    async def send_message(
            self,
            chat_id: int,
            text: str,
            **kwargs
    ) -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            **kwargs
        }
        return await self.make_request(
            http_method="get", method="sendMessage", params=payload
        )

    async def send_message_obj(self, chat_id: int, text: str) -> SendMessageResponse:
        message = await self.send_message(chat_id, text)
        return SendMessageResponse.Schema().load(message)

    async def answer_callback_query(
            self,
            callback_query_id: str,
            text: None | str = None,
            show_alert: None | bool = None,
            **kwargs
    ) -> dict:
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
            **kwargs
        }
        return await self.make_request(
            http_method="get", method="answerCallbackQuery", params=payload
        )

    async def edit_message(
            self, chat_id: int | str, message_id: int, text: str, reply_markup: dict, **kwargs
    ) -> dict:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": reply_markup,
            **kwargs
        }
        return await self.make_request(
            http_method="get", method="editMessageText", params=payload
        )
