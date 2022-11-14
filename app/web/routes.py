from typing import TYPE_CHECKING

from resources.ping.routes import setup_routes as ping_routes
from resources.quiz.routes import setup_routes as quiz_routes
from utils.url_paths import get_base_api_path


if TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application") -> None:
    base_path = get_base_api_path()

    ping_routes(app, base_path)
    quiz_routes(app, base_path)
