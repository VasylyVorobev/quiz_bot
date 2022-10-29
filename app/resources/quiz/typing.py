from dataclasses import dataclass


@dataclass
class GetProgrammingLanguages:
    count: int
    result: list[tuple[int, str]]


@dataclass
class QuizCreateResponse:
    question: tuple[int, str, int]
    answers: tuple[int, str, bool, int]


@dataclass
class QuestionsList:
    count: int
    result: list[tuple[int, str, int]]


@dataclass
class AnswersList:
    count: int
    result: list[tuple[int, str, bool, int]]


@dataclass
class QuizListResponse:
    questions: QuestionsList
    answers: list[tuple[int, str, bool, int]]
