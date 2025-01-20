from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

if TYPE_CHECKING:
    from .people import Cast, Crew


class Collection(TypedDict):
    id: int
    name: str
    poster_path: str | None
    backdrop_path: str | None


class Genre(TypedDict):
    id: int
    name: str


class ProductionCompany(TypedDict):
    id: int
    logo_path: str | None
    name: str
    origin_country: str # TODO(owocado): Literal[2 letter country codes uppercase]


class ProductionCountry(TypedDict):
    iso_3166_1: str # TODO(owocado): Literal[2 letter country codes uppercase]
    name: str


class SpokenLanguage(TypedDict):
    english_name: str
    iso_639_1: str # TODO(owocado): Literal[2 letter country codes]
    name: str


class Credits(TypedDict):
    cast: list[Cast]
    crew: list[Crew]


class MovieDetails(TypedDict):
    adult: bool
    backdrop_path: str | None
    belongs_to_collection: Collection | None
    budget: int | None
    genres: list[Genre]
    homepage: str | None
    id: int
    imdb_id: str | None
    origin_country: list[str]
    original_language: str
    original_title: str | None
    overview: str | None
    popularity: float
    poster_path: str | None
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    release_date: str | None
    revenue: int | None
    runtime: int | None
    spoken_languages: list[SpokenLanguage]
    status: Literal['Released', 'Post Production']
    tagline: str | None
    title: str
    video: bool
    vote_average: float
    vote_count: int
    credits: NotRequired[Credits]


