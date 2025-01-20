from __future__ import annotations

import datetime
import io
import logging
import math
from typing import TYPE_CHECKING, Literal

import discord
import msgspec
from box.box import Box
from discord.utils import format_dt, utcnow
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.embed import random_colour

from .api.base import CDN_BASE, CelebrityCast, MediaNotFound, format_date
from .api.constants import API_BASE, TMDB_ICON
from .api.details import MovieDetails, TVShowDetails

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from redbot.core.bot import Red

    from .api.person import Person
    from .types.movie import MovieDetails as MoviePayload
    from .types.tvshow import TVShow as TVShowPayload

GENDERS = (
    '',
    '\N{FEMALE SIGN}\N{VARIATION SELECTOR-16}',
    '\N{MALE SIGN}\N{VARIATION SELECTOR-16}',
    '\N{MALE WITH STROKE AND MALE AND FEMALE SIGN}',
)

logger = logging.getLogger('moviedb.utils')


# credits to devon (Gorialis)
def natural_size(value: int) -> str:
    if value < 1_000:
        return str(value)

    units: tuple[str, ...] = ('', 'K', ' million', ' billion')
    power = int(math.log(max(abs(value), 1), 1000))
    return f'{value / (1000 ** power):.1f}{units[power]}'


def make_person_embed(person: Person, colour: discord.Colour | int) -> discord.Embed:
    emb = discord.Embed(colour=colour, title=person.name)
    # emb.description = shorten(person.biography or "", 500, placeholder=" …")
    emb.url = f'https://themoviedb.org/person/{person.id}'
    emb.set_thumbnail(url=person.person_image)
    out = io.StringIO()
    if bio := person.biography:
        out.write(f"{bio[:500] + ' …' if len(bio) > 500 else bio}\n\n")
    out.write(f'**` Known for  `**  ` {person.known_for_department} `\n')
    if person.place_of_birth:
        out.write(f'**` Birthplace `**  ` {person.place_of_birth} `\n')
    if dob := person.birthday:
        out.write(f"**` Birthday   `**  {format_date(dob, 'D')} ({format_date(dob)})\n")
    if rip := person.deathday:
        out.write(f"**` Died on    `**  {format_date(rip, 'D')} ({format_date(rip)})\n")
    ext_links = []
    if person.imdb_id:
        ext_links.append(f'[` IMDb `](https://imdb.com/name/{person.imdb_id})')
    if person.homepage:
        ext_links.append(f'[` Website `]({person.homepage})\n')
    if ext_links:
        out.write(f"**` Links      `**  {'  '.join(ext_links)}\n")
    emb.description = out.getvalue()
    out.close()
    ext_links.clear()
    #  emb.set_footer(text="Data provided by TheMovieDB!", icon_url=TMDB_ICON)
    return emb


def parse_credits(cast_data: list[CelebrityCast], colour: discord.Colour | int, title: str, tmdb_id: str):
    pretty_cast = '\n'.join(
        f"**`[{idx:>2}]`**  {GENDERS[actor.gender or 0]}"
        f" [{actor.name}]({actor.tmdb_url}) as **{actor.character or '???'}**"
        for idx, actor in enumerate(cast_data, start=1)
    )

    pages: list[discord.Embed] = []
    idx = 1
    for page in pagify(pretty_cast, page_length=1500):
        emb = discord.Embed(colour=colour, description=page)
        tmdb_url = f'https://themoviedb.org/{tmdb_id}/cast'
        emb.set_author(name=f'{title} (Cast)', url=tmdb_url)
        emb.set_footer(
            text=f'Celebrities Cast • Page {idx}',
            icon_url=TMDB_ICON,
        )
        pages.append(emb)
        idx += 1

    return pages


def make_movie_embed(data: MovieDetails, colour: discord.Colour | int) -> discord.Embed:
    em = discord.Embed(colour=random_colour() or colour)
    year, _, _ = (data.release_date or '').partition('-')
    year = f' ({year})' if year else ''
    em.set_author(name=f'{data.title} {year}', url=data.tmdb_url)
    out = io.StringIO()
    #  if data.original_title != data.title:
        #  out.write(f'-# **{data.original_title}**\n')
    if data.tagline:
        out.write(f'-# *{data.tagline}*\n')
    if data.overview:
        out.write(f'\n{data.get_short_overview(200)}\n\n')
    #  if imdb_id := data.imdb_id:
        #  out.write(f'- **[IMDb](https://imdb.com/title/{imdb_id})**\n')
    #  em.url = f'https://themoviedb.org/movie/{data.id}'
    em.set_image(url=f"{CDN_BASE}{data.backdrop_path or '/'}")
    em.set_thumbnail(url=f"{CDN_BASE}{data.poster_path or '/'}")
    if data.humanize_runtime:
        out.write(f'- **Runtime:**  {data.humanize_runtime}\n')
    if rd := data.release_date:
        y, m, d = rd.split('-')
        dt = datetime.datetime(int(y), int(m), int(d), tzinfo=datetime.UTC)
        oc = f' ({data.origin_country[0]})' if data.origin_country else ''
        state = 'Released' if utcnow() > dt else 'Upcoming'
        out.write(f'- **{state}:**  {format_dt(dt, style="R")} • {format_dt(dt, style="d")}{oc}\n')
    if data.budget:
        out.write(f'- **Budget:**  (USD) ${natural_size(data.budget)}\n')
    if data.revenue:
        out.write(f'- **Revenue:**  (USD) ${natural_size(data.revenue)}\n')
    if data.vote_average and data.vote_count:
        out.write(f'- **Rating:**  {data.humanize_votes}\n')
    if data.genres:
        out.write(f'- **Genres:**  {data.all_genres}\n')
    if data.spoken_languages:
        en_only = len(data.spoken_languages) == 1 and data.spoken_languages[0].iso_639_1 == 'en'
        if not en_only:
            s = 's' if len(data.spoken_languages) > 1 else ''
            out.write(f'- **Language{s}:**  {data.all_spoken_languages}\n')
    if data.production_companies:
        s = 's' if len(data.production_companies) > 1 else ''
        out.write(f'- **Studio{s}:**  {data.all_production_companies}\n')
    ext_links = ' • '.join(
        f'**[{k}]({v})**'
        for k, v in (
            ('Letterboxd', f'https://letterboxd.com/tmdb/{data.id}'),
            ('IMDb', data.imdb_url),
            ('Homepage', data.homepage),
        )
        if v
    )
    if ext_links:
        out.write(f'- **Links:**  {ext_links}\n')
    em.description = out.getvalue()
    out.close()
    #  em.set_footer(text='See next page for more info on this movie!', icon_url=TMDB_ICON)
    return em


def make_tvshow_embed(data: TVShowDetails, colour: discord.Colour | int) -> discord.Embed:
    em = discord.Embed(colour=random_colour() or colour)
    out = io.StringIO()
    if data.tagline:
        out.write(f'-# *{data.tagline}*\n')
    if data.overview:
        out.write(f'\n{data.get_short_overview(200)}\n\n')
    #  em.url = f'https://themoviedb.org/tv/{data.id}'
    year, _, _ = (data.first_air_date or '').partition('-')
    year = f' ({year})' if year else ''
    em.set_author(name=f'{data.title} {year}', url=data.tmdb_url)
    em.set_image(url=f"{CDN_BASE}{data.backdrop_path or '/'}")
    em.set_thumbnail(url=f"{CDN_BASE}{data.poster_path or '/'}")
    if data.created_by:
        s = 's' if len(data.created_by) > 1 else ''
        out.write(f'- **Creator{s}:**  {data.creators}\n')
    if data.status:
        out.write(f'- **Status:**  {data.status} ({data.type})\n')
    #  if data.in_production:
        #  out.write('- **In production:**  ✅ Yes\n')
    if first_air_date := data.first_air_date:
        out.write(f'- **First aired:**  {format_date(first_air_date)}\n')
    if last_air_date := data.last_air_date:
        out.write(f'- **Last aired:**  {format_date(last_air_date)}\n')
    if data.number_of_seasons:
        out.write(f'- **Season{"s" if data.number_of_seasons > 1 else ""}:**  {data.seasons_count}\n')
    if runtime := data.episode_run_time:
        out.write(f'- **Avg. episode runtime:**  {runtime[0]} minutes\n')
    if data.genres:
        out.write(f'- **Genres:**  {data.all_genres}\n')
    #  if data.vote_average and data.vote_count:
        #  out.write(f'- **TMDB rating:**  {data.humanize_votes}\n')
    if data.networks:
        out.write(f'- **Networks:**  {data.all_networks}\n')
    if data.spoken_languages:
        out.write(f'- **Spoken languages:**  {data.all_spoken_languages}\n')
    if data.production_companies:
        s = 's' if len(data.production_companies) > 1 else ''
        out.write(f'- **Studio{s}:**  {data.all_production_companies}\n')
    em.description = out.getvalue()
    out.close()
    if data.seasons:
        for page in pagify(data.all_seasons, page_length=1024):
            em.add_field(name='Seasons', value=page, inline=True)
    if data.next_episode_to_air:
        em.add_field(name='Next Episode', value=data.next_episode_info, inline=False)
    #  em.set_footer(text='See next page for more info on this series!', icon_url=TMDB_ICON)
    return em


def gen_movie_or_tvshow_embed(data: MovieDetails | TVShowDetails):
    if isinstance(data, MovieDetails):
        return make_movie_embed(data, 0)
    if isinstance(data, TVShowDetails):
        return make_tvshow_embed(data, 0)


async def fetch_movie(session: ClientSession, api_key: str, movie_id: int | str):
    try:
        async with session.get(
            f'{API_BASE}/movie/{movie_id}',
            params={'api_key': api_key, 'append_to_response': 'credits,videos'},
        ) as resp:
            code = resp.status
            if code in (401, 404):
                err_data = await resp.json(loads=discord.utils._from_json)
                raise MediaNotFound(status_message=err_data['status_message'], status_code=code)
            if code != 200:
                raise MediaNotFound(status_message='', status_code=code)
            movie_data: MoviePayload = await resp.json(loads=discord.utils._from_json)
    except Exception:
        raise MediaNotFound(status_message='⚠️ Operation timed out.', status_code=408) from None
    else:
        return movie_data


async def fetch_tv_show(session: ClientSession, api_key: str, tvshow_id: int | str):
    tvshow_data = {}
    try:
        async with session.get(
            f'{API_BASE}/tv/{tvshow_id}',
            params={'api_key': api_key, 'append_to_response': 'credits,videos'},
        ) as resp:
            code = resp.status
            if code in (401, 404):
                err_data = await resp.json(loads=discord.utils._from_json)
                raise MediaNotFound(status_message=err_data['status_message'], status_code=code)
            if code != 200:
                raise MediaNotFound(status_message='', status_code=code)
            tvshow_data: TVShowPayload = await resp.json(loads=discord.utils._from_json)
    except Exception:
        raise MediaNotFound(status_message='⚠️ Operation timed out.', status_code=408) from None

    return tvshow_data


async def fetch_multi(bot: Red, key: str, *, item_id: int, media_type: Literal['movie', 'tv']):
    if media_type == 'movie':
        try:
            obj = await fetch_movie(bot.session, key, item_id)
        except MediaNotFound as err:
            raise err
        try:
            movie = msgspec.convert(obj, MovieDetails, strict=False, from_attributes=True)
        except Exception as ee:
            logger.debug('%s', obj)
            logger.error('msgspec convert failed for movie %s:', item_id, exc_info=ee)
            movie: MovieDetails = Box(obj)  # type: ignore
        return movie
    elif media_type == 'tv':
        try:
            obj = await fetch_tv_show(bot.session, key, item_id)
        except MediaNotFound as err:
            raise err
        try:
            tvshow = msgspec.convert(obj, TVShowDetails, strict=False, from_attributes=True)
        except Exception as ee:
            logger.debug('%s', obj)
            logger.error('msgspec convert failed for tvshow %s:', item_id, exc_info=ee)
            tvshow: TVShowDetails = Box(obj)  # type: ignore
        return tvshow

