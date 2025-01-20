from typing import Literal, TypedDict


GENDER = Literal[0, 1, 2, 3]


class Base(TypedDict):
    id: int
    adult: bool
    media_type: Literal['person', 'movie', 'tv']
    poster_path: str | None
    backdrop_path: str | None
    popularity: float


class Mixin(Base, total=False):
    overview: str
    original_language: str
    genre_ids: list[str]
    vote_average: float
    vote_count: int


class Movie(Mixin, total=False):
    title: str
    original_title: str | None
    release_date: str | None
    video: bool


class TV(Mixin, total=False):
    name: str
    original_name: str | None
    first_air_date: str | None
    origin_country: list[str]


class Person(Base, total=False):
    name: str
    original_name: str | None
    gender: GENDER
    known_for_department: str
    known_for: list[Movie | TV]


class MultiResult(Movie, TV, Person):
    ...

