from __future__ import annotations

import datetime

import discord
import msgspec
from discord.utils import escape_markdown

#  from .base import MediaNotFound as NotFound
from .constants import CDN_BASE


_MAP: dict[str, str] = {'tv': 'TV', 'movie': 'Movie'}


class BaseCredits(msgspec.Struct):
    adult: bool
    id: int
    media_type: str
    name: str | None = None
    original_name: str | None = None
    title: str | None = None
    original_title: str | None = None
    episode_count: int | None = None
    first_air_date: str | None = None
    release_date: str | None = None
    origin_country: list[str] = msgspec.field(default_factory=list)

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
    character: str | None = None

    @property
    def portray_as(self) -> str:
        if not self.character:
            return f'[{self.clean_title}]({self.tmdb_url})'
        return f'as {self.character} in [{self.clean_title}]({self.tmdb_url})'

    @property
    def pretty_format(self) -> str:
        return f"`{self.year or  ' ???'}`  ·  {self.portray_as} ({_MAP[self.media_type]})"


class CrewCredits(BaseCredits):
    department: str | None = None
    job: str | None = None

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
    popularity: float
    imdb_id: str | None = None
    biography: str | None = None
    known_for_department: str | None = None
    birthday: str | None = None
    deathday: str | None = None
    place_of_birth: str | None = None
    profile_path: str | None = None
    homepage: str | None = None
    #  combined_credits: PersonCredits | None = None
    also_known_as: list[str] = msgspec.field(default_factory=list)

    @property
    def birth_date(self):
        return discord.utils.parse_time(self.birthday) if self.birthday else None

    @property
    def death_date(self):
        return discord.utils.parse_time(self.deathday) if self.deathday else None

    @property
    def age(self):
        return self.calculate_age()

    def calculate_age(self):
        birthday = self.birthday
        if not birthday:
            return None

        birth_date = datetime.date.fromisoformat(birthday)
        today = discord.utils.utcnow()

        age = today.year - birth_date.year

        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1

        return age

    @property
    def image_url(self) -> str | None:
        return f'{CDN_BASE}{self.profile_path}' if self.profile_path else None

