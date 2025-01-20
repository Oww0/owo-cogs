from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, Optional, Self, Union, cast

import cachebox
import discord
import msgspec
from redbot.core.utils.views import ListPages
from box.box import Box
from redbot.core.utils.embed import random_colour
#  from redbot.core.utils.menus import EphemeralPagesView

from .api.base import MediaNotFound
from .api.constants import API_BASE, CDN_BASE, TMDB_ICON
from .api.person import Person
from .utils import fetch_multi, gen_movie_or_tvshow_embed, make_person_embed

if TYPE_CHECKING:
    from discord import Interaction, SelectOption
    from redbot.core.bot import Red

    from .api.details import MovieDetails, TVShowDetails
    from .moviedb import MovieDB


logger = logging.getLogger('moviedb.views')


class OfferSelect(discord.ui.Select):
    view: ChoiceView

    def __init__(self, *, options: list[SelectOption], placeholder: str) -> None:
        super().__init__(options=options, placeholder=placeholder)

    async def callback(self, i: Interaction[Red]) -> None:
        value = int(self.values[0])
        if value == self.view.result:
            await i.response.send_message('Thats what is being currently shown :P', ephemeral=True)
            return

        self.view.result = value
        em = self.view._cache.get(value)
        if em:
            if i.user.id == self.view.author_id:
                await i.edit_original_response(embed=em, view=self.view)
            else:
                await i.response.send_message(embed=em, ephemeral=True)
            return

        try:
            person = await self.view.fetch_person(i, value)
        except MediaNotFound as err:
            await i.response.send_message(str(err), ephemeral=True)
            return
        em = make_person_embed(person, random_colour())
        if i.user.id == self.view.author_id:
            await i.edit_original_response(embed=em, view=self.view)
        else:
            await i.response.send_message(embed=em, ephemeral=True)
        return


class ChoiceView(discord.ui.View):
    """
    This can be used in command converters where you offer a list of choices to the user
    and user need to pick an entry.
    """

    def __init__(
        self,
        *,
        options: list[SelectOption],
        author_id: int,
        result_id: int,
        placeholder: str,
        timeout: float = 600,
    ) -> None:
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.result: int = result_id
        self._cache: cachebox.Cache[int, discord.Embed] = cachebox.Cache(0)
        self.add_item(OfferSelect(options=options, placeholder=placeholder))

    async def on_error(self, i: Interaction[Red], error: Exception, item: discord.ui.Item[Self]):
        self.stop()
        if not self._cache.is_empty():
            self._cache.clear()
        logger.error('ChoiceView errored on item %s:', item.__class__.__name__, exc_info=error)
        if i.response.is_done():
            await i.followup.send('oh fuck my shitcode exploded', ephemeral=True)
        else:
            await i.response.send_message('oh fuck my code exploded', ephemeral=True)

    async def on_timeout(self) -> None:
        if not self._cache.is_empty():
            self._cache.clear()
        self.stop()

    async def fetch_person(self, i: discord.Interaction[Red], person_id: int) -> Person:
        api_key = (await i.client.get_shared_api_tokens('tmdb')).get('api_key', '')
        try:
            async with i.client.session.get(
                f'{API_BASE}/person/{person_id}',
                params={'api_key': api_key, 'append_to_response': 'combined_credits'},
            ) as resp:
                if resp.status in (401, 404):
                    data = await resp.json(loads=discord.utils._from_json)
                    raise MediaNotFound(**data)
                if resp.status != 200:
                    raise MediaNotFound(status_message='😔 No results found.', status_code=resp.status)
                person_data: dict = await resp.json(loads=discord.utils._from_json)
        except Exception:
            raise MediaNotFound(status_message='Operation timed out!', status_code=408) from None

        try:
            person = msgspec.convert(person_data, Person, strict=False)
        except Exception as err:
            logger.warning('Error in msgspec.convert to type Person:', exc_info=err)
            person: Person = Box(person_data) # type: ignore

        return person


class CastButton(discord.ui.Button):
    view: TVMovieView

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row,
        )

    async def callback(self, itx: Interaction[Red]) -> None:
        item = self.view.current_item
        if not item.cast:
            await itx.response.send_message(
                'Looks like TMDB is missing cast data for this one, someone go update xD',
                ephemeral=True,
            )

        pages: list[discord.Embed] = []
        for idx, cs in enumerate(item.cast, 1):
            em = discord.Embed(color=discord.Colour.dark_embed())
            em.set_author(name=cs.name, url=cs.tmdb_url)
            em.description = f'-# _as **{cs.character}**_'
            if cs.profile_path:
                em.set_image(url=f'{CDN_BASE}{cs.profile_path}')
            em.set_footer(
                text=f'Celebrities Cast • Page {idx} of {item.total_cast}',
                icon_url=TMDB_ICON,
            )
            pages.append(em)

        from lyrics.views import InteractionPaginationView as EphemeralPagesView

        await EphemeralPagesView(ListPages(pages), ctx=itx).start(itx, ephemeral=True)


class CrewButton(discord.ui.Button):
    view: TVMovieView

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row,
        )

    async def callback(self, itx: Interaction[Red]) -> None:
        item = self.view.current_item
        if not item.crew:
            await itx.response.send_message(
                'Looks like TMDB is missing cast data for this one, someone go update xD',
                ephemeral=True,
            )

        pages: list[discord.Embed] = []
        for idx, cs in enumerate(item.crew, 1):
            em = discord.Embed(color=discord.Colour.dark_embed())
            em.set_author(name=cs.name, url=cs.tmdb_url)
            em.description = f'-# _{cs.job}_'
            if cs.profile_path:
                em.set_image(url=f'{CDN_BASE}{cs.profile_path}')
            em.set_footer(
                text=f'All Crew • Page {idx} of {item.total_crew}',
                icon_url=TMDB_ICON,
            )
            pages.append(em)

        from lyrics.views import InteractionPaginationView as EphemeralPagesView

        await EphemeralPagesView(ListPages(pages), ctx=itx).start(itx, ephemeral=True)


class TrailerButton(discord.ui.Button):
    view: TVMovieView

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            emoji=emoji,
            row=row,
        )

    async def callback(self, itx: Interaction[Red]) -> None:
        item = self.view.current_item
        if not item.videos or (item.videos and not item.videos.results):
            await itx.followup.send('Looks like trailers for this are missing on TMDB xD', ephemeral=True)
            return

        pages: list[str] = []
        for obj in sorted(item.videos.results, key=lambda x: x.publish_date):
            pages.append(
                f'{obj.site_emoji} **{obj}** | <:clock:1266353462325547008> Published '
                f'{discord.utils.format_dt(obj.publish_date, "R")}'
            )

        from lyrics.views import InteractionPaginationView as EphemeralPagesView

        await EphemeralPagesView(ListPages(pages), ctx=itx).start(itx, ephemeral=True)


class TVMovieSelect(discord.ui.Select):
    view: TVMovieView

    def __init__(self, *, options: list[SelectOption], placeholder: str, row: int | None = None) -> None:
        super().__init__(options=options, placeholder=placeholder, row=row)

    async def callback(self, i: Interaction[Red]) -> None:
        if TYPE_CHECKING:
            assert isinstance(i.client.cogs['MovieDB'], MovieDB)

        iid, _, mtype = self.values[0].partition('_')
        if TYPE_CHECKING:
            mtype = cast(Literal['movie', 'tv'], mtype)
        value = int(iid)
        if value == self.view.current_item.id:
            await i.response.send_message('That entry is currently shown in above embed xD', ephemeral=True)
            return
        if i.user.id != self.view.author_id:
            await i.response.send_message(
                f'Only <@{self.view.author_id}> can use this dropdown. You can use the buttons :D',
                ephemeral=True,
            )
            return

    #  async def process_send(self, i: Interaction[Red], value: int):
        cache = self.view._cache.get(value)
        if cache:
            em1 = gen_movie_or_tvshow_embed(cache)
            self.view.current_item = cache
            self.view._update_buttons()
            await self.view.message.edit(embeds=[em1], view=self.view)
            return

        env = await i.client.get_shared_api_tokens('tmdb')
        data = await fetch_multi(i.client, env['api_key'], item_id=value, media_type=mtype)
        em1 = gen_movie_or_tvshow_embed(data)
        self.view._cache[data.id] = self.view.current_item = data
        self.view._update_buttons()
        try:
            await self.view.message.edit(embeds=[em1], view=self.view)
        except Exception:
            await i.followup.send(embed=em1, ephemeral=True)
        return


class TVMovieView(discord.ui.View):

    def __init__(
        self,
        *,
        author_id: int,
        timeout: float = 600,
        source: MovieDetails | TVShowDetails,
        message: discord.Message = discord.utils.MISSING,
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.message = message
        self._cache: cachebox.Cache[int, MovieDetails | TVShowDetails] = cachebox.Cache(0)
        self._cache[source.id] = source
        self.current_item = source
        self.cast_button = CastButton(label=f'Cast ({source.total_cast})')
        self.crew_button = CrewButton(label=f'Crew ({source.total_crew})')
        self.trailer_btn = TrailerButton(label=f'Trailers ({len(source.videos.results)})')
        if source.cast:
            self.add_item(self.cast_button)
        if source.crew:
            self.add_item(self.crew_button)
        if source.videos.results:
            self.add_item(self.trailer_btn)
        #  self.add_item(TVMovieSelect(options=options, placeholder=placeholder))

    def _update_buttons(self):
        if self.current_item.cast:
            self.cast_button.label = f'Cast ({self.current_item.total_cast})'
            self.cast_button.disabled = False
        else:
            self.cast_button.label = 'Cast (0)'
            self.cast_button.disabled = True
        if self.current_item.crew:
            self.crew_button.label = f'Crew ({self.current_item.total_crew})'
            self.crew_button.disabled = False
        else:
            self.crew_button.label = 'Crew (0)'
            self.crew_button.disabled = True
        if self.current_item.videos.results:
            self.trailer_btn.label = f'Trailers ({len(self.current_item.videos.results)})'
            self.trailer_btn.disabled = False
        else:
            self.trailer_btn.label = 'Trailers'
            self.trailer_btn.disabled = True

    async def on_error(self, i: Interaction[Red], error: Exception, item: discord.ui.Item[Self]):
        self.stop()
        if not self._cache.is_empty():
            self._cache.clear()
        logger.error('TVMovieView errored on item %s:', item.__class__.__name__, exc_info=error)
        if i.response.is_done():
            await i.followup.send('oh fuck shitcode exploded', ephemeral=True)
        else:
            await i.response.send_message('oh fuck my code exploded', ephemeral=True)

    async def on_timeout(self) -> None:
        if not self._cache.is_empty():
            self._cache.clear()
        self.stop()

    async def interaction_check(self, i: Interaction, /) -> bool:
        await i.response.defer()
        return True

