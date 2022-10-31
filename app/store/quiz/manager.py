from json import dumps

from aiohttp.web_exceptions import HTTPBadRequest

from resources.quiz.schemas import QuizCreateSchema
from resources.quiz.typing import QuizCreateResponse, QuizListResponse
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

    async def create_quiz(self, quiz_data: QuizCreateSchema) -> QuizCreateResponse:
        async with self.app.store.db.engine.begin() as conn:
            question = await self.question.create_question(
                quiz_data.language_id,
                quiz_data.title,
                conn
            )
            answers = await self.answer.create_answers(quiz_data.answers, question[0], conn)
            await conn.commit()
            return QuizCreateResponse(**{
                "question": question,
                "answers": answers
            })

    async def get_quizzes(self, limit: int, offset: int) -> QuizListResponse:
        questions = await self.question.get_questions(limit, offset)
        if not questions.result and questions.count > 0:
            raise HTTPBadRequest(
                text=dumps({"detail": "Such a programming language already exists"})
            )
        questions_id = list(zip(*questions.result))[0] if questions.result else ()
        answers = (await self.answer.get_answers(questions_id=questions_id)).result
        return QuizListResponse(
            questions=questions,
            answers=answers
        )
