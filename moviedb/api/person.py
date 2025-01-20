from __future__ import annotations

#  from typing import TYPE_CHECKING, Any

#  import discord
import msgspec
from discord.utils import escape_markdown

#  from .base import MediaNotFound as NotFound
from .constants import CDN_BASE

#  if TYPE_CHECKING:
    #  import aiohttp

_MAP: dict[str, str] = {'tv': 'TV', 'movie': 'Movie'}


class BaseCredits(msgspec.Struct):
    adult: bool
    id: int
    origin_country: list[str] | None
    name: str | None
    original_name: str | None
    title: str | None
    original_title: str | None
    episode_count: int | None
    first_air_date: str | None
    release_date: str | None
    media_type: str

    @property
    def clean_title(self) -> str:
        return escape_markdown(self.title or self.name or '')

    @property
    def year(self) -> int:
        date = self.first_air_date or self.release_date
        return int(date.split('-')[0]) if date and '-' in date else 0

    @property
    def tmdb_url(self) -> str:
        return f'https://themoviedb.org/{self.media_type}/{self.id}'


class CastCredits(BaseCredits):
    character: str | None

    @property
    def portray_as(self) -> str:
        if not self.character:
            return f'[{self.clean_title}]({self.tmdb_url})'
        return f'as {self.character} in [{self.clean_title}]({self.tmdb_url})'

    @property
    def pretty_format(self) -> str:
        return f"`{self.year or  ' ???'}`  ·  {self.portray_as} ({_MAP[self.media_type]})"


class CrewCredits(BaseCredits):
    department: str | None
    job: str | None

    @property
    def portray_as(self) -> str:
        if not self.job:
            return f'[{self.clean_title}]({self.tmdb_url})'
        return f'as {self.job} in [{self.clean_title}]({self.tmdb_url})'

    @property
    def pretty_format(self) -> str:
        return f"`{self.year or ' ???'}`  ·  {self.portray_as} ({_MAP[self.media_type]})"


class PersonCredits(msgspec.Struct, omit_defaults=True):
    cast: list[CastCredits] = msgspec.field(default_factory=list)
    crew: list[CrewCredits] = msgspec.field(default_factory=list)


class Person(msgspec.Struct, omit_defaults=True):
    id: int
    name: str
    gender: int
    adult: bool
    imdb_id: str | None
    biography: str | None
    known_for_department: str | None
    popularity: float
    birthday: str | None
    deathday: str | None
    place_of_birth: str | None
    profile_path: str | None
    homepage: str | None
    #  combined_credits: PersonCredits | None
    also_known_as: list[str] = msgspec.field(default_factory=list)

    @property
    def person_image(self) -> str:
        return f'{CDN_BASE}{self.profile_path}' if self.profile_path else ''

    #  @classmethod
    #  async def request(cls, session: aiohttp.ClientSession, api_key: str, person_id: Any) -> Person:
        #  try:
            #  async with session.get(
                #  f'{API_BASE}/person/{person_id}',
                #  params={'api_key': api_key, 'append_to_response': 'combined_credits'},
            #  ) as resp:
                #  if resp.status in (401, 404):
                    #  data = await resp.json(loads=discord.utils._from_json)
                    #  raise NotFound(**data)
                #  if resp.status != 200:
                    #  raise NotFound(status_message='No results found.', status_code=resp.status)
                #  person_data: dict = await resp.json(loads=discord.utils._from_json)
        #  except Exception:
            #  raise NotFound(status_message='Operation timed out!', status_code=408) from None

        #  return dacite.from_dict(data_class=cls, data=person_data)
