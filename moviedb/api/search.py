from __future__ import annotations

#  from operator import itemgetter
from typing import Literal

import msgspec

from .constants import GENDERS, MOVIE_GENRES, TV_GENRES

#  if TYPE_CHECKING:
    #  from aiohttp import ClientSession


class KnownFor(msgspec.Struct):
    name: str | None = None
    title: str | None = ''

    @property
    def human_title(self):
        return self.name or self.title or ''


class PersonSearch(msgspec.Struct, omit_defaults=True):
    adult: bool
    id: int
    name: str
    gender: Literal[0, 1, 2, 3]
    media_type: Literal['person']
    original_name: str | None = None
    known_for: list[KnownFor] = msgspec.field(default_factory=list)

    @property
    def famous_for(self) -> str:
        if not self.known_for:
            return ''
        return f'known for {", ".join(x.human_title for x in self.known_for)}'

    @property
    def gender_emoji(self):
        return GENDERS[self.gender]


class CommonSearchMixinForMovieTV(msgspec.Struct, kw_only=True):
    id: int
    media_type: Literal['movie', 'tv']
    adult: bool
    original_language: str
    genre_ids: list[int]
    popularity: float
    vote_average: float
    vote_count: int
    backdrop_path: str | None = None
    overview: str | None = None
    poster_path: str | None = None

    @property
    def human_type(self):
        return 'movie' if self.media_type == 'movie' else 'series'

    def get_short_overview(self, chars: int = 100):
        if not self.overview:
            return ''
        return f'{self.overview[:chars - 4]}...' if len(self.overview) > chars else self.overview


class MovieSearch(CommonSearchMixinForMovieTV):
    title: str
    original_title: str
    release_date: str | None = None
    video: bool | None = None

    @property
    def genres(self):
        if not self.genre_ids:
            return ''
        return ', '.join(MOVIE_GENRES.get(gid, f'Genre{gid}') for gid in self.genre_ids)

    @property
    def year(self):
        year, _, _ = (self.release_date or '').partition('-')
        return year


class TVShowSearch(CommonSearchMixinForMovieTV):
    name: str
    original_name: str
    first_air_date: str | None = None

    @property
    def genres(self):
        if not self.genre_ids:
            return ''
        return ', '.join(TV_GENRES.get(gid, f'Genre{gid}') for gid in self.genre_ids)

    @property
    def title(self) -> str:
        return self.name or self.original_name

    @property
    def year(self):
        year, _, _ = (self.first_air_date or '').partition('-')
        return year

