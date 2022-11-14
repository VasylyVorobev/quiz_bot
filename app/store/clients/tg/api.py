from typing import cast

from aiohttp import ClientSession

from store.tg.dcs import GetUpdatesResponse, SendMessageResponse


class TgClient:
    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str, session: ClientSession):
        self.token = token
        self.session = session

    def get_url(self, method: str) -> str:
        return f"{self.BASE_URL}{self.token}/{method}"

    async def get_me(self) -> dict:
        async with self.session.get(self.get_url("getMe")) as resp:
            return await resp.json()

    async def get_updates(self, offset: None | int = None, timeout: int = 0) -> dict:
        params = {}
        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout
        async with self.session.get(self.get_url("getUpdates"), params=params) as resp:
            res = await resp.json()
            return res

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
        async with self.session.get(self.get_url("sendMessage"), json=payload) as resp:
            return await resp.json()

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
        async with self.session.get(self.get_url("answerCallbackQuery"), json=payload) as resp:
            return await resp.json()
