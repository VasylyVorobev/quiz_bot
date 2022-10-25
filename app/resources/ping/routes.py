from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application", base_api_path: str) -> None:
    from resources.ping.views import PingView

    app.router.add_view(f"{base_api_path}/ping", PingView)
