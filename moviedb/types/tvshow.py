from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .movie import Credits, Genre, ProductionCompany, ProductionCountry, SpokenLanguage


class Creator(TypedDict):
    id: int
    credit_id: str
    name: str
    original_name: str
    gender: Literal[0, 1, 2, 3]
    profile_path: str | None


class LastEpisode(TypedDict):
    id: int
    name: str
    overview: str
    vote_average: float
    vote_count: int
    air_date: str
    episode_number: int
    episode_type: str
    production_code: str
    runtime: int | None
    season_number: int
    show_id: int
    still_path: str | None


class Network(TypedDict):
    id: int
    logo_path: str
    name: str
    origin_country: str


class Season(TypedDict):
    air_date: str
    episode_count: int
    id: int
    name: str
    overview: str
    poster_path: str | None
    season_number: int
    vote_average: float


class TVShow(TypedDict, total=False):
    adult: bool
    backdrop_path: str | None
    created_by: list[Creator]
    episode_run_time: list[int]
    first_air_date: str | None
    genres: list[Genre]
    homepage: str
    id: int
    in_production: Literal[True, False]
    languages: list[str]
    last_air_date: str
    last_episode_to_air: LastEpisode
    name: str
    next_episode_to_air: LastEpisode | None
    networks: list[Network]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str | None
    popularity: float
    poster_path: str | None
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    seasons: list[Season]
    spoken_languages: list[SpokenLanguage]
    status: Literal['Canceled', 'Returning Series', 'Ended']
    tagline: str
    type: Literal['Scripted']
    vote_average: float
    vote_count: int
    credits: Credits

