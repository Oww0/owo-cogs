from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
import msgspec

if TYPE_CHECKING:
    import aiohttp

    from ..types.search import MultiResult


API_BASE = 'https://api.themoviedb.org/3'
CDN_BASE = 'https://image.tmdb.org/t/p/original'

__all__ = (
    'BaseSearch',
    'CelebrityCast',
    'Genre',
    'Language',
    'MediaNotFound',
    'ProductionCompany',
    'ProductionCountry',
    'multi_search',
)


class MediaNotFound(BaseException):

    __slots__: tuple[str, ...] = ('http_code', 'status_message', 'status_code', 'success')

    def __init__(
        self,
        *,
        status_message: str,
        http_code: int | None = None,
        status_code: int | None = None,
        success: bool = False,
    ):
        self.http_code = http_code
        self.status_code = status_code
        self.status_message = status_message
        self.success = success
        super().__init__(self.status_message or f'https://http.cat/{self.http_code}.jpg')


class BaseSearch(msgspec.Struct):
    id: int
    adult: bool
    popularity: float
    media_type: Literal['movie', 'tv', 'person']
    vote_count: int
    vote_average: float
    backdrop_path: str | None = None
    overview: str | None = None
    poster_path: str | None = None


class CelebrityCast(msgspec.Struct):
    adult: bool
    id: int
    known_for_department: str
    name: str
    original_name: str
    character: str
    credit_id: str
    order: int
    gender: Literal[0, 1, 2, 3] | None = None
    popularity: float | None = None
    profile_path: str | None = None
    #  cast_id: int | None = None

    @property
    def tmdb_url(self):
        return f'https://www.themoviedb.org/person/{self.id}'


class Genre(msgspec.Struct):
    id: int
    name: str


class ProductionCompany(msgspec.Struct):
    id: int
    name: str
    logo_path: str | None = None
    origin_country: str | None = None


class ProductionCountry(msgspec.Struct):
    iso_3166_1: str
    name: str


class Language(msgspec.Struct):
    name: str
    iso_639_1: str
    english_name: str | None = None

    def __str__(self) -> str:
        return self.english_name or self.name


class Trailer(msgspec.Struct):
    iso_639_1: str
    iso_3166_1: str
    name: str
    key: str
    site: Literal['YouTube', 'Vimeo']
    type: Literal['Trailer', 'Teaser', 'Clip', 'Bloopers', 'Featurette', 'Behind the Scenes']
    official: bool
    published_at: str # in datetime.isoformat() format

    def __str__(self) -> str:
        return f'[{self.site} {self.type}]({self.url})'

    @property
    def publish_date(self):
        return discord.utils.parse_time(self.published_at)

    @property
    def site_emoji(self):
        if self.site == 'YouTube':
            return '<:youtube:1266345035209768981>'
        elif self.site == 'Vimeo':
            return '<:vimeo:1330827258981646386>'
        else:
            return '<:rock_sus:1304004353790574642>'

    @property
    def url(self):
        if self.site == 'YouTube':
            return f'https://youtu.be/{self.key}'
        elif self.site == 'Vimeo':
            return f'https://vimeo.com/{self.key}'
        else:
            return ''


def format_date(
    date: str | None,
    style: Literal['f', 'F', 'd', 'D', 't', 'T', 'R'] = 'R',
    *,
    prefix: str = '',
) -> str:
    if not date:
        return ''
    return prefix + discord.utils.format_dt(discord.utils.parse_time(date), style=style)


async def multi_search(
    session: aiohttp.ClientSession,
    api_key: str,
    query: str,
    include_adult: Literal['true', 'false'] = 'false',
) -> list[MultiResult]:
    try:
        async with session.get(
            f'{API_BASE}/search/multi',
            params={'api_key': api_key, 'query': query, 'include_adult': include_adult},
        ) as resp:
            code = resp.status
            if resp.status in (401, 404):
                data = await resp.json(loads=discord.utils._from_json)
                raise MediaNotFound(**data)
            if resp.status != 200:
                raise MediaNotFound(status_message=f'😔 No results found (code {code})', status_code=code)
            all_data: dict = await resp.json(loads=discord.utils._from_json)
    except Exception as ee:
        raise MediaNotFound(status_message=f'Operation timed out: {ee}', status_code=408) from ee

    if 'results' not in all_data:
        raise MediaNotFound(status_message='😔 TMDB returned zero results for your query.', status_code=404)
    return all_data.get('results', [])
