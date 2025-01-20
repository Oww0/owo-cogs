from __future__ import annotations

from datetime import UTC, datetime
from textwrap import shorten
from typing import TYPE_CHECKING

import discord
import msgspec
from discord.app_commands import Choice
from redbot.core import commands

from .api.base import MediaNotFound, multi_search
from .api.details import MovieDetails, TVShowDetails
from .api.search import MovieSearch, TVShowSearch
from .utils import format_date

if TYPE_CHECKING:
    from redbot.core.bot import Red
    from redbot.core.commands import Context


class MovieFinder(discord.app_commands.Transformer):

    async def convert(self, ctx: Context[Red], argument: str):
        api_key = (await ctx.bot.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(ctx.bot.session, api_key, argument)
        except MediaNotFound as err:
            raise commands.BadArgument(str(err)) from err

        results = [
            msgspec.convert(obj, MovieSearch, strict=False, from_attributes=True)
            for obj in all_data if obj['media_type'] == 'movie'
        ]
        if not results:
            raise commands.BadArgument('⛔ No such movie found from given query.')
        if len(results) == 1:
            return await MovieDetails.request(ctx.bot.session, api_key, results[0].id)

        # https://github.com/Sitryk/sitcogsv3/blob/master/lyrics/lyrics.py#L142
        items = [f"{i}.  {obj.title} ({format_date(obj.release_date, 'd')})" for i, obj in enumerate(results, start=1)]
        prompt: discord.Message = await ctx.send(
            f'Found below {len(items)} movies. Choose one in 60 seconds:\n\n' + '\n'.join(items).replace(' ()', '')
        )

        def check(msg: discord.Message) -> bool:
            return bool(
                msg.content
                and msg.content.isdigit()
                and int(msg.content) in range(len(items) + 1)
                and msg.author.id == ctx.author.id
                and msg.channel.id == ctx.channel.id
            )

        try:
            choice = await ctx.bot.wait_for('message', timeout=60, check=check)
        except TimeoutError:
            choice = None

        if choice is None or (choice.content and choice.content.strip() == '0'):
            try:
                await prompt.delete()
            except Exception:
                pass
            raise commands.BadArgument("‼ You didn't pick a valid choice. Operation cancelled.")

        try:
            await prompt.delete()
        except Exception:
            pass
        movie_id = results[int(choice.content.strip()) - 1].id
        return await MovieDetails.request(ctx.bot.session, api_key, movie_id)

    async def transform(self, i: discord.Interaction[Red], value: str):
        key = (await i.client.get_shared_api_tokens('tmdb')).get('api_key', '')
        return await MovieDetails.request(i.client.session, key, value)

    async def autocomplete(self, i: discord.Interaction[Red], value: str) -> list[Choice[str]]:
        token = (await i.client.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(i.client.session, token, value)
        except MediaNotFound:
            return []

        results = [
            msgspec.convert(obj, MovieSearch, strict=False, from_attributes=True)
            for obj in all_data if obj['media_type'] == 'movie'
        ]
        if not results:
            return []

        def parser(title: str, date: str | None) -> str:
            if not date:
                return shorten(title, 94)
            date = datetime.strptime(date, '%Y-%m-%d').astimezone(UTC).strftime('%d %b, %Y')
            return f"{shorten(title, 75, placeholder=' …')} ({date})"

        choices = [Choice(name=f'{parser(movie.title, movie.release_date)}', value=str(movie.id)) for movie in results]
        return choices[:24] if len(choices) > 25 else choices


class TVShowFinder(discord.app_commands.Transformer):

    async def convert(self, ctx: Context[Red], argument: str):
        api_key = (await ctx.bot.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(ctx.bot.session, api_key, argument)
        except MediaNotFound as err:
            raise commands.BadArgument(str(err)) from err

        results = [
            msgspec.convert(obj, TVShowSearch, strict=False, from_attributes=True)
            for obj in all_data if obj['media_type'] == 'tv'
        ]

        if not results:
            raise commands.BadArgument('⛔ No such TV show found from given query.')
        if len(results) == 1:
            return await TVShowDetails.request(ctx.bot.session, api_key, results[0].id)

        # https://github.com/Sitryk/sitcogsv3/blob/master/lyrics/lyrics.py#L142
        items = [
            f"{i}.  {v.name or v.original_name}"
            f" ({format_date(v.first_air_date, 'd', prefix='started on ')})"
            for i, v in enumerate(results, start=1)
        ]
        prompt: discord.Message = await ctx.send(
            f'Found below {len(items)} TV shows. Choose one in 60 seconds:\n\n' + '\n'.join(items).replace(' ()', '')
        )

        def check(msg: discord.Message) -> bool:
            return bool(
                msg.content
                and msg.content.isdigit()
                and int(msg.content) in range(len(items) + 1)
                and msg.author.id == ctx.author.id
                and msg.channel.id == ctx.channel.id
            )

        try:
            choice = await ctx.bot.wait_for('message', timeout=60, check=check)
        except TimeoutError:
            choice = None

        if choice is None or (choice.content and choice.content.strip() == '0'):
            try:
                await prompt.delete()
            except Exception:
                pass
            raise commands.BadArgument("‼ You didn't pick a valid choice. Operation cancelled.")

        try:
            await prompt.delete()
        except Exception:
            pass
        tv_id = results[int(choice.content.strip()) - 1].id
        return await TVShowDetails.request(ctx.bot.session, api_key, tv_id)

    async def transform(self, i: discord.Interaction[Red], value: str):
        key = (await i.client.get_shared_api_tokens('tmdb')).get('api_key', '')
        return await TVShowDetails.request(i.client.session, key, value)

    async def autocomplete(self, i: discord.Interaction[Red], value: str) -> list[Choice[str]]:
        if not value:
            return []

        token = (await i.client.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            all_data = await multi_search(i.client.session, token, value)
        except MediaNotFound:
            return []

        results = [
            msgspec.convert(obj, TVShowSearch, strict=False, from_attributes=True)
            for obj in all_data if obj['media_type'] == 'tv'
        ]
        if not results:
            return []

        def parser(title: str, date: str | None) -> str:
            if not date:
                return shorten(title, 94)
            date = datetime.strptime(date, '%Y-%m-%d').astimezone(UTC).strftime('%d %b, %Y')
            return f'{shorten(title, 75)} (began on {date})'

        choices = [
            Choice(name=f'{parser(tvshow.name, tvshow.first_air_date)}', value=str(tvshow.id)) for tvshow in results
        ]
        return choices[:24] if len(choices) > 25 else choices

