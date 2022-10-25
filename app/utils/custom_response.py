from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response


def json_response(
    data: dict,
    http_status: int = 200,
    status: str = "ok",
):
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "data": data
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: None | str = None,
    data: None | dict = None
) -> Response:
    data = data or {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": message,
            "data": data
        }
    )
