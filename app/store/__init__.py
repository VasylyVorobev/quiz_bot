import typing

from store.database.database import Database

if typing.TYPE_CHECKING:
    from web.app import Application


class Store:

    def __init__(self, app: "Application"):
        from store.quiz.manager import QuizManager

        self.quiz = QuizManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    app.store = Store(app)
