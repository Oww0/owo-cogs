import io

import discord
from redbot.core import commands

from .converter import MapFlags

MAP_TYPES: tuple[str, ...] = ("roadmap", "satellite", "terrain", "hybrid")


class Maps(commands.Cog):
    """Fetch a Google map of a specific location with zoom and map types."""

    __authors__ = ("<@306810730055729152>",)
    __version__ = "2.1.2"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        return (
            f"{super().format_help_for_context(ctx)}\n\n"
            f"Authors:  {', '.join(self.__authors__)}\n"
            f"Cog version:  v{self.__version__}"
        )

    @commands.bot_has_permissions(attach_files=True)
    @commands.command()
    async def map(self, ctx: commands.Context, *, flags: MapFlags) -> None:
        """Fetch map of a location from Google Maps.

        **Zoom level:**
        `zoom` parameter value must be from level 1 to 20. Defaults to 12.
        Below zoom levels that will show the approximate level of detail:
        ```prolog
         1 to  4 : World
         5 to  9 : Landmass or continent
        10 to 14 : City
        15 to 19 : Streets
        20       : Buildings
        ```

        **Map types:**
        - `maptype` parameter accepts only below 4 values:
         - `roadmap`, `satellite`, `terrain`, `hybrid`
         - Defaults to `roadmap` if invalid value provided
         - See Google's online [docs](https://developers.google.com/maps/documentation/maps-static/start) for more information.

        **Example:**
        - `[p]map new york -zoom 17 -maptype hybrid`
        - `[p]map jumeirah beach dubai -maptype terrain`
        - `[p]map niagara falls canada -zoom 15 -maptype satellite`
        """
        api_key = (await ctx.bot.get_shared_api_tokens("googlemaps")).get("api_key")
        if not api_key:
            await ctx.send("⚠️ Bot owner need to set API key first!", ephemeral=True)
            return

        location, zoom, map_type = flags.location, flags.zoom, flags.maptype
        if not location:
            await ctx.send("You need to provide a location name silly", ephemeral=True)
            return
        zoom = zoom if (1 <= zoom <= 20) else 12
        map_type = "roadmap" if map_type not in MAP_TYPES else map_type

        await ctx.typing()
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "center": location,
            "zoom": zoom,
            "size": "640x640",
            "scale": "2",
            "format": "png32",
            "maptype": map_type,
            "key": api_key,
        }
        if map_type == "roadmap":
            params["style"] = "feature:road.highway|element:labels.text.fill|visibility:on|color:0xffffff"
        try:
            async with ctx.bot.session.get(base_url, params=params) as response:
                if response.status != 200:
                    await ctx.send(f"https://http.cat/{response.status}")
                    return
                image = io.BytesIO(await response.read())
                image.seek(0)
        except Exception as error:
            await ctx.send(f"Operation timed out: {error}")
            return

        url = f"<https://www.google.com/maps/search/{location.replace(' ', '+')}>"
        await ctx.send(url, file=discord.File(image, "google_maps.png"))
        image.close()
        return
