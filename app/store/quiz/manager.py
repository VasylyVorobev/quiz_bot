from json import dumps

from aiohttp.web_exceptions import HTTPBadRequest
from sqlalchemy import select

from resources.quiz.schemas import QuizCreateSchema
from resources.quiz.typing import QuizCreateResponse, QuizListResponse
from resources.quiz.models import questions, answers, questions_users
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
            answers_ = await self.answer.create_answers(quiz_data.answers, question[0], conn)
            await conn.commit()
            return QuizCreateResponse(**{
                "question": question,
                "answers": answers_
            })

    async def get_quizzes(self, limit: int, offset: int) -> QuizListResponse:
        questions_ = await self.question.get_questions(limit, offset)
        if not questions_.result and questions_.count > 0:
            raise HTTPBadRequest(
                text=dumps({"detail": "Such a programming language already exists"})
            )

        questions_id = next(zip(*questions_.result), ())
        answers_ = (await self.answer.get_answers(questions_id=questions_id)).result
        return QuizListResponse(
            questions=questions_,
            answers=answers_
        )

    async def get_first_unanswered_quiz_for_user(
            self,
            language_id: int,
            user_id: int
    ) -> None | QuizCreateResponse:

        answered_questions_query = (
            select([questions_users.c.question])
            .select_from(
                questions_users
                .join(questions, questions_users.c.question == questions.c.id)
            )
            .where(
                (questions_users.c.user == user_id) &
                (questions_users.c.is_correct.is_(True)) &
                (questions.c.language == language_id)
            )
        )

        query = (
            select([questions.c.id, questions.c.title, questions.c.language])
            .where(
                (questions.c.language == language_id) &
                (questions.c.id.not_in(answered_questions_query))
            )
            .limit(1)
        )

        async with self.app.store.db.engine.begin() as conn:
            question = (await conn.execute(query)).fetchone()
            if not question:
                # All {language_id} questions answered
                return

            question_answers = (
                select(answers)
                .where(answers.c.question == question[0])
            )
            answers_ = (await conn.execute(question_answers)).fetchall()
            return QuizCreateResponse(question=question, answers=answers_)
