import logging
import typing

if typing.TYPE_CHECKING:
    from .app import Application


def setup_logging(app: "Application") -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    app.logger = logging.getLogger(__name__)
