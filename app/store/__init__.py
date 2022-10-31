import typing

from store.database.database import Database
from store.queue.accessor import BaseQueue
from store.quiz.manager import QuizManager
from store.tg.accessor import TgAccessor
from store.user.accessor import UserAccessor

if typing.TYPE_CHECKING:
    from web.app import Application


class Store:

    def __init__(self, app: "Application"):
        self.db = Database(app)
        app.on_startup.append(self.db.connect)
        app.on_shutdown.append(self.db.disconnect)

        self.quiz = QuizManager(app)
        self.tg = TgAccessor(app)
        self.queue = BaseQueue(app)
        self.user = UserAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
