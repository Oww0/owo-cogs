from typing import Literal, TypedDict


class Rating(TypedDict):
    aggregate_rating: float
    votes_count: int


class Title(TypedDict, total=False):
    id: str
    type: Literal['movie']
    primary_title: str
    start_year: int
    plot: str
    genres: list[str]
    rating: Rating | None


class IMDbData(TypedDict):
    title: Title

