from typing import cast


class TestCreateQuiz:
    async def test_create_quiz_success(self, cli, store, get_programming_language):
        question_count = await store.quiz.question.get_questions_count()
        answers_count = await store.quiz.answer.get_answers_count()
        language_id, _ = get_programming_language
        data = {
            "language_id": language_id,
            "title": "Question ?",
            "answers": [
                {
                    "title": "Answer 1",
                    "is_correct": True
                },
                {
                    "title": "Answer 2",
                    "is_correct": False
                }
            ]
        }
        resp = await cli.post("/api/v1/quiz/", json=data)
        assert resp.status == 201
        assert await store.quiz.question.get_questions_count() == (question_count + 1)
        assert await store.quiz.answer.get_answers_count() == (answers_count + 2)

        response_data = await resp.json()
        assert response_data["status"] == "ok"
        assert response_data["data"]["id"] is not None
        assert response_data["data"]["title"] == data["title"]
        assert response_data["data"]["language_id"] == data["language_id"]

    async def test_create_quiz_few_correct_answers(self, cli, get_programming_language):
        language_id, _ = get_programming_language
        data = {
            "language_id": language_id,
            "title": "Question ?",
            "answers": [
                {
                    "title": "Answer 1",
                    "is_correct": True
                },
                {
                    "title": "Answer 2",
                    "is_correct": True
                }
            ]
        }
        resp = await cli.post("/api/v1/quiz/", json=data)
        assert resp.status == 400

    async def test_create_quiz_invalid_language(self, cli):
        data = {
            "language_id": 999,
            "title": "Question ?",
            "answers": [
                {
                    "title": "Answer 1",
                    "is_correct": True
                },
                {
                    "title": "Answer 2",
                    "is_correct": False
                }
            ]
        }
        resp = await cli.post("/api/v1/quiz/", json=data)
        assert resp.status == 400

        data["answers"][0]["is_correct"] = False
        resp = await cli.post("/api/v1/quiz/", json=data)
        assert resp.status == 400

    async def test_create_quiz_few_answers(self, cli, get_programming_language):
        language_id, _ = get_programming_language

        data = {
            "language_id": language_id,
            "title": "Question ?",
            "answers": [
                {
                    "title": "Answer 1",
                    "is_correct": True
                }
            ]
        }
        resp = await cli.post("/api/v1/quiz/", json=data)
        assert resp.status == 400


class TestListQuiz:
    async def test_list_quiz_success(self, cli, create_quizzes):
        quizzes = cast(list, create_quizzes)
        resp = await cli.get("/api/v1/quiz/")
        assert resp.status == 200

        data = await resp.json()

        assert data["status"] == "ok"
        assert data["data"]["count"] == len(quizzes)
