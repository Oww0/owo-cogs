from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

import discord
import msgspec
from discord.utils import utcnow

from .base import CelebrityCast, Genre, Language, ProductionCompany, ProductionCountry, Trailer # noqa
from ..utils import format_date

if TYPE_CHECKING:
    from redbot.core.bot import Red

    from ..types.imdbapi import IMDbData

MISSING = discord.utils.MISSING


class MovieCrew(msgspec.Struct, omit_defaults=True):
    adult: bool
    gender: Literal[0, 1, 2, 3]
    id: int
    known_for_department: str
    name: str
    original_name: str | None
    popularity: float
    profile_path: str | None
    credit_id: str
    department: str
    job: str

    @property
    def tmdb_url(self):
        return f'https://www.themoviedb.org/person/{self.id}'


class Credits(msgspec.Struct, omit_defaults=True):
    cast: list[CelebrityCast] = msgspec.field(default_factory=list)
    crew: list[MovieCrew] = msgspec.field(default_factory=list)


class VideoResult(msgspec.Struct, omit_defaults=True):
    results: list[Trailer] = msgspec.field(default_factory=list)


class CommonMixin(msgspec.Struct, kw_only=True, omit_defaults=True):
    adult: bool
    backdrop_path: str | None
    credits: Credits
    homepage: str | None
    id: int
    original_language: str
    overview: str | None
    popularity: float | None
    poster_path: str | None
    status: str
    tagline: str | None
    vote_average: float | None
    vote_count: int | None
    videos: VideoResult
    genres: list[Genre] = msgspec.field(default_factory=list)
    production_companies: list[ProductionCompany] = msgspec.field(default_factory=list)
    production_countries: list[ProductionCountry] = msgspec.field(default_factory=list)

    @property
    def cast(self):
        return self.credits.cast if self.credits else MISSING

    @property
    def crew(self):
        return self.credits.crew if self.credits else MISSING

    @property
    def total_cast(self):
        return len(self.cast) if self.cast else 0

    @property
    def total_crew(self):
        return len(self.crew) if self.crew else 0

    @property
    def trailers(self):
        return [tr for tr in self.videos.results if tr.type == 'Trailer'] if self.videos else []

    def get_short_overview(self, chars: int = 100):
        if not self.overview:
            return ''
        return f'{self.overview[:chars - 4]}...' if len(self.overview) > chars else self.overview


class MovieDetails(CommonMixin, omit_defaults=True):
    budget: int | None
    imdb_id: str | None
    original_title: str
    release_date: str | None
    revenue: int | None
    runtime: int | None
    title: str
    video: bool
    spoken_languages: list[Language] = msgspec.field(default_factory=list)
    origin_country: list[str] = msgspec.field(default_factory=list)

    @property
    def all_genres(self) -> str:
        return ', '.join(g.name for g in self.genres)

    @property
    def all_production_companies(self) -> str:
        return ', '.join(g.name for g in self.production_companies)

    @property
    def all_production_countries(self) -> str:
        return ', '.join(g.name for g in self.production_countries)

    @property
    def all_spoken_languages(self) -> str:
        return ', '.join(str(g) for g in self.spoken_languages)

    @property
    def humanize_runtime(self) -> str:
        if not self.runtime:
            return ''
        h, m = self.runtime // 60, self.runtime % 60
        hours, minutes = f'{h} hr' if h else '', f'{m} mins' if m else ''
        return f'{hours} {minutes}'

    @property
    def humanize_votes(self) -> str:
        votes = self.vote_count
        if not votes:
            return f':star: **{self.vote_average:.1f}** '
        num = f'{votes / 1000:.1f}K' if votes > 999 else str(votes)
        return f':star: **{self.vote_average:.1f}** ({num} votes)'

    @property
    def imdb_url(self):
        return f'https://imdb.com/title/{self.imdb_id}' if self.imdb_id else None

    @property
    def media_type(self) -> Literal['movie', 'tv']:
        return 'movie'

    @property
    def tmdb_url(self):
        return f'https://themoviedb.org/movie/{self.id}'

    @classmethod
    async def get_imdb_rating(cls, bot: Red):
        if not cls.imdb_id:
            return 0.0

        from .constants import IMDBAPI_GQL_QUERY

        try:
            async with bot.session.post(
                'https://graph.imdbapi.dev/v1',
                json={'query': IMDBAPI_GQL_QUERY, 'variables': {"IMDB_ID": cls.imdb_id}},
                headers={'user-agent': 'merlin @ discord (user_id: 830676830419157002)'}
            ) as r:
                if r.status != 200:
                    return 0.0
                data: dict[Literal['data'], IMDbData] = await r.json()
        except Exception:
            return 0.0

        try:
            rating = data['data']['title']['rating']
            return rating['aggregate_rating'] if rating else 0.0
        except KeyError:
            return 0.0


class Creator(msgspec.Struct):
    id: int
    credit_id: str
    name: str
    gender: int
    profile_path: str | None


class EpisodeInfo(msgspec.Struct):
    id: int
    name: str
    overview: str
    vote_average: float | None
    vote_count: int | None
    air_date: str | None
    episode_number: int
    production_code: str
    runtime: int | None
    season_number: int
    still_path: str | None
    show_id: int | None


class Network(msgspec.Struct):
    id: int
    name: str
    logo_path: str | None
    origin_country: str | None


class Season(msgspec.Struct, omit_defaults=True):
    id: int
    name: str
    air_date: str | None
    overview: str
    episode_count: int
    poster_path: str | None
    season_number: int = 0
    vote_average: float = 0.0

    @property
    def release_date(self) -> datetime | None:
        return datetime.fromisoformat(self.air_date) if self.air_date else None

    @property
    def prefix(self) -> str:
        if not self.release_date:
            return ''
        return 'airing' if self.release_date.timestamp() > utcnow().timestamp() else 'aired'


class TVShowDetails(CommonMixin, omit_defaults=True):
    first_air_date: str | None
    in_production: bool
    last_air_date: str | None
    last_episode_to_air: EpisodeInfo | None
    name: str
    next_episode_to_air: EpisodeInfo | None
    number_of_episodes: int | None
    number_of_seasons: int | None
    original_language: str | None
    original_name: str
    type: str | None
    created_by: list[Creator] = msgspec.field(default_factory=list)
    episode_run_time: list[int] = msgspec.field(default_factory=list)
    seasons: list[Season] = msgspec.field(default_factory=list)
    languages: list[str] = msgspec.field(default_factory=list)
    networks: list[Network] = msgspec.field(default_factory=list)
    origin_country: list[str] = msgspec.field(default_factory=list)
    spoken_languages: list[Language] = msgspec.field(default_factory=list)

    @property
    def all_genres(self) -> str:
        return ', '.join(g.name for g in self.genres)

    @property
    def all_production_companies(self) -> str:
        return ', '.join(g.name for g in self.production_companies)

    @property
    def all_production_countries(self) -> str:
        return ', '.join(g.name for g in self.production_countries)

    @property
    def all_spoken_languages(self) -> str:
        return ', '.join(str(g) for g in self.spoken_languages)

    @property
    def all_networks(self) -> str:
        if len(self.networks) > 3:
            left = len(self.networks) - 3
            return f"{', '.join(n.name for n in self.networks[:3])} & {left} more!"
        return ', '.join(g.name for g in self.networks)

    @property
    def all_seasons(self) -> str:
        return '\n'.join(
            f'{i}. {tv.name}{format_date(tv.air_date, prefix=f", {tv.prefix} ")}'
            f"  ({tv.episode_count or 0} episodes)"
            for i, tv in enumerate(self.seasons, start=1)
        )

    @property
    def creators(self) -> str:
        return ', '.join(c.name for c in self.created_by)

    @property
    def humanize_votes(self) -> str:
        votes = self.vote_count
        if not votes:
            return f':star: **{self.vote_average:.1f}** '
        num = f'{votes / 1000:.1f}K' if votes > 999 else str(votes)
        return f':star: **{self.vote_average:.1f}** ({num} votes)'

    @property
    def media_type(self) -> Literal['movie', 'tv']:
        return 'tv'

    @property
    def next_episode_info(self) -> str:
        if not self.next_episode_to_air:
            return ''

        next_ep = self.next_episode_to_air
        next_airing = 'ETA unknown!'
        if next_ep.air_date:
            next_airing = format_date(next_ep.air_date, prefix='likely airing ')
        return (
            f'**S{next_ep.season_number or 0}E{next_ep.episode_number or 0}**'
            f' : {next_airing}\n**Titled as:** {next_ep.name}'
        )

    @property
    def seasons_count(self) -> str:
        return f'{self.number_of_seasons} ({self.number_of_episodes} episodes)'

    @property
    def title(self) -> str:
        return self.name

    @property
    def original_title(self):
        return self.original_name

    @property
    def tmdb_url(self):
        return f'https://themoviedb.org/tv/{self.id}'

