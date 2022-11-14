from aiohttp_apispec import docs, response_schema

from resources.ping.schemas import PingSchema
from resources.base_view import View
from utils.custom_response import json_response


class PingView(View):

    @docs(tags=["Health check"], summary="Health check")
    @response_schema(PingSchema())
    async def get(self):
        return json_response(data={"ping": "pong"})
