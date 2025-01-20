from __future__ import annotations

from typing import Literal, TypedDict


class Crew(TypedDict, total=False):
    adult: bool
    gender: Literal[0, 1, 2, 3]
    id: int
    known_for_department: Literal[
        'Acting',
        'Production',
        'Art',
        'Costume & Make-Up',
        'Directing',
        'Writing',
        'Editing',
        'Sound',
        'Camera',
        'Visual Effects',
        'Crew',
        'Lighting',
    ]
    name: str
    original_name: str | None
    popularity: float
    profile_path: str | None
    credit_id: str
    department: str
    job: str


class Cast(Crew, total=False):
    cast_id: int
    character: str
    order: int


class Person(TypedDict):
    adult: bool
    also_known_as: list[str]
    biography: str | None
    birthday: str | None
    deathday: str | None
    gender: Literal[0, 1, 2, 3]
    homepage: str | None
    id: int
    imdb_id: str | None
    known_for_department: str
    name: str
    place_of_birth: str | None
    popularity: float
    profile_path: str | None

