import discord
from redbot.core import commands


class MapFlags(commands.FlagConverter, prefix="-", delimiter=" "):
    location: str | None = commands.flag(
        default=None,
        description="Input a location name that is available on Google Maps.",
        positional=True,
    )
    zoom: int = commands.flag(
        default=12,
        description="Zoom level of the map, from 1 to 20. Defaults to 12.",
        max_args=1,
    )
    map_type: str = commands.flag(
        default="roadmap",
        description="The type or format of the map, either 'roadmap' (default), 'satellite', 'terrain' or 'hybrid'",
        max_args=1,
    )
