from __future__ import annotations
from typing import TYPE_CHECKING

from redbot.core.errors import CogLoadError

from .maps import Maps

if TYPE_CHECKING:
    from redbot.core.bot import Red

__red_end_user_data_statement__ = "This cog does not persistently store data about users."


async def setup(bot: Red) -> None:
    if not getattr(bot, "session", None):
        raise CogLoadError("This cog requires bot.session attr to be set.")
    await bot.add_cog(Maps())
