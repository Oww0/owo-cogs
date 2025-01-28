from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import cachebox
import discord
import msgspec
from box.box import Box
from discord.app_commands import describe
from redbot.core import commands

from .api.base import MediaNotFound, multi_search
from .api.constants import API_BASE
from .api.person import Person
from .api.search import MovieSearch, PersonSearch, TVShowSearch
from .utils import fetch_multi, gen_movie_or_tvshow_embed, make_person_embed
from .views import ChoiceView, TVMovieSelect, TVMovieView

if TYPE_CHECKING:
    from redbot.core.bot import Red
    from redbot.core.commands import Context

    from .api.details import MovieDetails, TVShowDetails
    from .types.people import Person as PersonPayload


COLOR = discord.Colour(0xC57FFF)

logger = logging.getLogger('moviedb.core')


class MovieDB(commands.Cog):
    """Get summarized info about a movie or TV show/series."""

    __authors__ = '<@306810730055729152>'
    __version__ = '5.0.0'

    def __init__(self, *args: Any, **kwargs: Any):
        self._cache: cachebox.TTLCache[
            int, MovieDetails | Person | TVShowDetails
        ] = cachebox.TTLCache(0, 1800)

    async def cog_unload(self) -> None:
        self._cache.clear()

    def format_help_for_context(self, ctx: Context[Red]) -> str:  # Thanks Sinbad!
        return (
            f'{super().format_help_for_context(ctx)}\n\n'
            f'**Author(s):** {self.__authors__}\n'
            f'**Cog version:** {self.__version__}'
        )

    async def red_delete_data_for_user(self, **kwargs: Any) -> None:
        """Nothing to delete"""
        pass

    @commands.bot_has_permissions(embed_links=True)
    @commands.hybrid_command(aliases=['actor', 'director', 'celeb'])
    @describe(name='Enter celebrity actor/director name. Be concise for accurate results!')
    async def celebrity(self, ctx: Context[Red], *, name: str) -> None:
        """Get info about a movie/tvshow celebrity or crew!"""

        await ctx.defer()
        api_key = (await ctx.bot.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(ctx.bot.session, api_key, name)
        except MediaNotFound as err:
            raise commands.BadArgument(str(err)) from err

        results = [
            msgspec.convert(obj, PersonSearch, strict=False, from_attributes=True)
            for obj in all_data if obj['media_type'] == 'person'
        ]
        if not results:
            raise commands.BadArgument('⛔ No celebrities could be found from given input.')

        person_id =  results[0].id
        try:
            person = await self.fetch_person(ctx.bot, api_key, person_id)
        except MediaNotFound as err:
            raise commands.BadArgument(str(err)) from None

        emb1 = make_person_embed(person, COLOR)

        try:
            from notsobot.utils import get_prominent_color

            async with ctx.bot.session.get(person.image_url) as r:
                buf = await r.read()
            clr = await asyncio.to_thread(get_prominent_color, buf)
        except Exception:
            pass
        else:
            emb1.colour = clr

        count = len(results)
        if count > 1:
            view = ChoiceView(
                options=[
                    discord.SelectOption(
                        label=f'{obj.gender_emoji} {obj.name}',
                        value=str(obj.id),
                        description=obj.famous_for if len(obj.famous_for) < 100 else f'{obj.famous_for[:96]}...',
                    )
                    for obj in results
                ],
                author_id=ctx.author.id,
                result_id=person_id,
                placeholder=f'Check out other {count - 1} celebrities...'
            )
            out = await ctx.send(embeds=[emb1], view=view)
            await view.wait()
            try:
                await out.edit(view=None)
            except Exception:
                logger.exception('Error editing message: %s\n %s', out.jump_url, out.to_dict())
                pass
        else:
            await ctx.send(embed=emb1)

    @staticmethod
    async def fetch_person(bot: Red, key: str, person_id: int) -> Person:
        try:
            async with bot.session.get(
                f'{API_BASE}/person/{person_id}',
                params={'api_key': key}, # , 'append_to_response': 'combined_credits'
            ) as resp:
                code = resp.status
                if code in (401, 404):
                    data = await resp.json(loads=discord.utils._from_json)
                    raise MediaNotFound(**data)
                if code != 200:
                    raise MediaNotFound(status_message='😔 No results found.', status_code=code)
                person_data: PersonPayload = await resp.json(loads=discord.utils._from_json)
        except Exception:
            raise MediaNotFound(status_message='Operation timed out!', status_code=408) from None

        try:
            person = msgspec.convert(person_data, Person, strict=False)
        except Exception as err:
            logger.warning('Error in msgspec.convert to type Person:', exc_info=err)
            person: Person = Box(person_data)  # type: ignore
        return person

    @commands.bot_has_permissions(embed_links=True)
    @commands.hybrid_command(aliases=('tmdb', 'imdb', 'tv', 'tvshow'))
    @describe(name='Search for movies or TV shows. Provide concise movie/series name to get accurate results.')
    async def movie(self, ctx: Context[Red], *, name: str):
        """Get info about a movie or TV series."""
        await ctx.typing()

        #  embeds: list[discord.Embed] = []
        api_key = (await ctx.bot.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(ctx.bot.session, api_key, name)
        except MediaNotFound as err:
            raise commands.BadArgument(str(err)) from err

        if not all_data:
            raise commands.BadArgument('⛔ No movie or TV series found.')

        results: list[MovieSearch | TVShowSearch] = []
            # msgspec.convert(obj, MovieSearch, strict=False, from_attributes=True)
        for obj in all_data:
            if obj['media_type'] == 'movie':
                try:
                    ms = msgspec.convert(obj, MovieSearch, strict=False, from_attributes=True)
                except Exception:
                    results.append(Box(obj))  # type: ignore
                else:
                    results.append(ms)
            elif obj['media_type'] == 'tv':
                try:
                    tvs = msgspec.convert(obj, TVShowSearch, strict=False, from_attributes=True)
                except Exception:
                    results.append(Box(obj))  # type: ignore
                else:
                    results.append(tvs)
            else:
                continue
        if not results:
            raise commands.BadArgument('⛔ No movie or TV series found, only celebs/crew people.')

        data = await fetch_multi(ctx.bot, api_key, item_id=results[0].id, media_type=results[0].media_type)
        em1 = await gen_movie_or_tvshow_embed(data, bot=ctx.bot)
        #  embeds.append(em1)

        view = TVMovieView(author_id=ctx.author.id, source=data)
        if len(results) > 1:
            view.add_item(
                TVMovieSelect(
                    options=self.gen_dropdown_options(results),
                    placeholder=f'Check out other {len(results) - 1} entries...'
                )
            )
        view.message = await ctx.send(embeds=[em1], view=view)
        await view.wait()
        try:
            await view.message.edit(view=None)
        except Exception:
            logger.exception('Error editing message: %s\n %s', view.message.jump_url, view.message.to_dict())
            pass

    @movie.error
    async def on_movie_error(self, ctx: Context[Red], error: commands.HybridCommandError):
        try:
            await ctx.send(str(error), ephemeral=True)
        except Exception:
            logger.warning('[%s] %s', error.__class__.__name__, error)

    @staticmethod
    def gen_dropdown_options(results: list[MovieSearch | TVShowSearch]):
        return [
            discord.SelectOption(
                label=pp.title if len(pp.title) < 100 else f'{pp.title[:96]}...',
                description=(
                    f'{pp.human_type.title()} • {pp.year or "Upcoming"}'
                    f' • {pp.genres or pp.get_short_overview(75) or "h"}'
                ),
                value=f'{pp.id}_{pp.media_type}',
            )
            for pp in results
        ]

