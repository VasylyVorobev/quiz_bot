from aiohttp_apispec import docs, response_schema

from resources.ping.schemas import PingSchema
from utils.custom_response import json_response
from web.app import View


class PingView(View):

    @docs(tags=["Health check"], summary="Health check")
    @response_schema(PingSchema())
    async def get(self):
        return json_response(data={"ping": "pong"})
