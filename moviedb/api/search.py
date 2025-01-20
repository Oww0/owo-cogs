from __future__ import annotations

#  from operator import itemgetter
from typing import Literal

import msgspec
from redbot.core.utils.chat_formatting import humanize_list

from .constants import MOVIE_GENRES, TV_GENRES

#  if TYPE_CHECKING:
    #  from aiohttp import ClientSession


class PersonSearch(msgspec.Struct, omit_defaults=True):
    adult: bool
    id: int
    name: str
    gender: int
    media_type: str
    popularity: float
    known_for_department: str | None
    original_name: str | None
    profile_path: str | None
    known_for: list[MovieSearch | TVShowSearch] = msgspec.field(default_factory=list)

    @property
    def famous_for(self) -> str:
        if not self.known_for:
            return ''
        return f'known for {humanize_list([x.title for x in self.known_for])}'


class CommonSearchMixinForMovieTV(msgspec.Struct):
    backdrop_path: str | None
    id: int
    overview: str | None
    poster_path: str | None
    media_type: Literal['movie', 'tv']
    adult: bool
    original_language: str
    genre_ids: list[int]
    popularity: float
    vote_average: float
    vote_count: int

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
    release_date: str | None
    video: bool | None

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
    first_air_date: str | None

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

