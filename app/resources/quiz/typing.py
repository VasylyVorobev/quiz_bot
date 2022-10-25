from typing import TypedDict


class GetProgrammingLanguages(TypedDict):
    count: int
    result: list[tuple[int, str]]
