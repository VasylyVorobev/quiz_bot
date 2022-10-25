from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application", base_api_path: str) -> None:
    from resources.quiz import views

    app.router.add_view(f"{base_api_path}/programming_language/", views.ProgrammingLanguageView)
    app.router.add_view(
        f"{base_api_path}/programming_language/{{id}}/",
        views.ProgrammingLanguageDetailView
    )

    app.router.add_view(f"{base_api_path}/questions/", views.QuestionView)
