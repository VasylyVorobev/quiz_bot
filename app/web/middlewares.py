import json
from typing import TYPE_CHECKING, Callable

from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import Response
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from utils.custom_response import error_json_response

if TYPE_CHECKING:
    from web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    422: "unprocessable_entity",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler: Callable) -> Response:
    try:
        return await handler(request)
    except HTTPException as exc:
        try:
            reason = json.loads(exc.text)
        except json.JSONDecodeError:
            reason = exc.text
        return error_json_response(
            http_status=exc.status,
            message=exc.reason,
            status=HTTP_ERROR_CODES[exc.status],
            data=reason if isinstance(reason, dict) else {"reason": reason}
        )


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
