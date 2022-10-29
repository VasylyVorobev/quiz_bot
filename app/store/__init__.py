import typing

from store.database.database import Database
from store.queue.accessor import BaseQueue
from store.quiz.manager import QuizManager
from store.tg.accessor import TgAccessor

if typing.TYPE_CHECKING:
    from web.app import Application


class Store:

    def __init__(self, app: "Application"):

        self.quiz = QuizManager(app)
        self.tg = TgAccessor(app)
        self.queue = BaseQueue(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    app.store = Store(app)
