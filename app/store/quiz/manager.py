# from resources.quiz.schemas import QuestionCreateSchema
from store.base.accessor import BaseAccessor
from store.quiz.services.programming_language import ProgrammingLanguageService
from store.quiz.services.question import QuestionService
from store.quiz.services.answer import AnswerService


class QuizManager(BaseAccessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.programming_language_service = ProgrammingLanguageService(self.app)
        self.question = QuestionService(self.app)
        self.answer = AnswerService(self.app)

    # async def create_quiz(self, quiz_data: QuestionCreateSchema):
    #     question_id, *_ = await self.question.create_question(
    #         quiz_data.language_id,
    #         quiz_data.title
    #     )
    #     answers = await self.answer.create_answers(quiz_data.answers)
