from json import dumps

from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import (
    request_schema,
    response_schema,
    docs,
    querystring_schema,
    match_info_schema
)

from utils.schemas_converting import schema_converter
from resources.base_view import View
from resources.quiz import schemas


class ProgrammingLanguageView(View):

    @docs(tags=["Programming Language"], summary="Creating a programming language")
    @request_schema(schemas.ProgrammingLanguageCreateSchema)
    @response_schema(schemas.ProgrammingLanguageCreateResponseSchema.Schema(), code=201)
    @schema_converter.convert_to_schema(schemas.ProgrammingLanguageCreateResponseSchema)
    async def post(self):
        title = self.data["title"]
        if result := await (
            self.store.quiz.programming_language_service
            .create_programming_language(title)
        ):
            return result, 201

        raise HTTPBadRequest(text=dumps({"detail": "Such a programming language already exists"}))

    @docs(tags=["Programming Language"], summary="Get all programming languages")
    @response_schema(schemas.ProgrammingLanguageListResponseSchema.Schema(), code=200)
    @querystring_schema(schemas.PageSchema)
    @schema_converter.convert_to_schema(schemas.ProgrammingLanguageListSchema)
    async def get(self):
        return await (
            self.store.quiz.programming_language_service
            .get_programming_languages(**self.request["querystring"])
        )


class ProgrammingLanguageDetailView(View):

    @docs(tags=["Programming Language"], summary="Get a programming language")
    @response_schema(schemas.ProgrammingLanguageCreateResponseSchema.Schema())
    @match_info_schema(schemas.ProgrammingLanguageMatchInfoSchema.Schema())
    @schema_converter.convert_to_schema(schemas.ProgrammingLanguageCreateResponseSchema)
    async def get(self):
        if result := await (
            self.store.quiz.programming_language_service
            .get_programming_language(self.request["match_info"].id)
        ):
            return result
        raise HTTPNotFound(text="Not found")

    @docs(tags=["Programming Language"], summary="Get a programming language")
    @response_schema(schemas.ProgrammingLanguageCreateResponseSchema.Schema())
    @match_info_schema(schemas.ProgrammingLanguageMatchInfoSchema.Schema())
    @request_schema(schemas.ProgrammingLanguageCreateSchema)
    @schema_converter.convert_to_schema(schemas.ProgrammingLanguageCreateResponseSchema)
    async def put(self):
        title = self.data["title"]
        if result := await (
                self.store.quiz.programming_language_service
                .update_programming_language(self.request["match_info"].id, title)
        ):
            return result
        raise HTTPNotFound(text=dumps({"detail": "Not found"}))


class QuizView(View):

    @docs(tags=["Quiz"], summary="List quizzes")
    @response_schema(schemas.QuizListResponseSchema.Schema())
    @querystring_schema(schemas.PageSchema)
    @schema_converter.convert_to_schema(schemas.QuizListSchema)
    async def get(self):
        return await self.store.quiz.get_quizzes(**self.request["querystring"])

    @docs(tags=["Quiz"], summary="Create a question")
    @request_schema(schemas.QuizCreateSchema.Schema())
    @response_schema(schemas.QuizDetailResponseSchema.Schema())
    @schema_converter.convert_to_schema(schemas.QuizCreateSchema)
    async def post(self):
        language_exists = await (
            self.store.quiz.programming_language_service
            .is_programming_language_exists(language_id=self.data.language_id)
        )
        if language_exists:
            return await self.store.quiz.create_quiz(self.data), 201
        raise HTTPBadRequest(text=dumps({"detail": "There is no such programming language."}))
