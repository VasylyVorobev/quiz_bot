import json
from typing import TYPE_CHECKING, Callable

from aiohttp.web_exceptions import (
    HTTPUnauthorized,
    HTTPForbidden,
    HTTPNotFound,
    HTTPNotImplemented,
    HTTPMethodNotAllowed,
    HTTPConflict,
    HTTPException,
    HTTPUnprocessableEntity
)
from aiohttp.web_response import Response
from aiohttp_apispec import validation_middleware
from aiohttp.web_middlewares import middleware

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
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler: Callable) -> Response:
    try:
        return await handler(request)
    except HTTPUnauthorized as e:
        return error_json_response(
            http_status=401, status=HTTP_ERROR_CODES[401], message=str(e)
        )
    except HTTPForbidden as e:
        return error_json_response(
            http_status=403, status=HTTP_ERROR_CODES[403], message=str(e)
        )
    except HTTPNotFound as e:
        return error_json_response(
            http_status=404, status=HTTP_ERROR_CODES[404], message=str(e)
        )
    except HTTPNotImplemented as e:
        return error_json_response(
            http_status=405, status=HTTP_ERROR_CODES[405], message=str(e)
        )
    except HTTPMethodNotAllowed as e:
        return error_json_response(
            http_status=405, status=HTTP_ERROR_CODES[405], message=str(e)
        )
    except HTTPConflict as e:
        return error_json_response(
            http_status=409, status=HTTP_ERROR_CODES[409], message=e.text
        )
    except HTTPException as e:
        return error_json_response(
            http_status=400, status=HTTP_ERROR_CODES[400], message=str(e), data={"detail": e.text}
        )
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    # except (Exception,) as e:
    #     return error_json_response(
    #         http_status=500, status=HTTP_ERROR_CODES[500], message=str(e)
    #     )


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
