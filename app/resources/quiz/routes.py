from typing import TYPE_CHECKING
from resources.quiz import views

if TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application", base_api_path: str) -> None:

    app.router.add_view(f"{base_api_path}/programming_language/", views.ProgrammingLanguageView)
    app.router.add_view(
        f"{base_api_path}/programming_language/{{id}}/",
        views.ProgrammingLanguageDetailView
    )

    app.router.add_view(f"{base_api_path}/quiz/", views.QuizView)
