# This is a slightly modified version of converter originally made by TrustyJAID for his NotSoBot cog
# Attribution at: https://github.com/TrustyJAID/Trusty-cogs/blob/master/notsobot/converter.py
# I have included original LICENSE notice bundled with this cog to adhere to the license terms.
# I am forever indebted to and wholeheartedly thank TrustyJAID for providing this converter.
import re

from typing import Pattern, List

import discord
from redbot.core import commands

IMAGE_LINKS: Pattern = re.compile(
    r"(https?:\/\/[^\"\'\s]*\.(?:png|jpg|jpeg|webp|gif)(\?size=[0-9]*)?)", flags=re.I
)


class ImageFinder(commands.Converter):
    """
    This is a class to convert NotSoBot's image searching
    capabilities into a more general converter class
    """

    async def convert(self, ctx: commands.Context, argument: str) -> List[str]:
        attachments = ctx.message.attachments
        matches = IMAGE_LINKS.finditer(argument)
        urls = []
        if matches:
            urls.extend(match.group(1) for match in matches)
        if attachments:
            urls.extend(
                match.group(1)
                for attachment in attachments
                if (match := IMAGE_LINKS.match(attachment.url))
            )

        return urls

    async def find_images_in_replies(self, reference: discord.Message) -> List[str]:
        urls = []
        if match := IMAGE_LINKS.search(reference.content):
            urls.append(match.group(1))
        if reference.attachments:
            if match := IMAGE_LINKS.match(reference.attachments[0].url):
                urls.append(match.group(1))
        if reference.embeds and reference.embeds[0].image:
            urls.append(reference.embeds[0].image.url)
        return urls

    async def search_for_images(self, ctx: commands.Context) -> List[str]:
        urls = []
        async for message in ctx.channel.history(limit=20):
            if message.embeds and message.embeds[0].image:
                urls.append(message.embeds[0].image.url)
            if message.attachments:
                urls.extend(
                    match.group(1)
                    for attachment in message.attachments
                    if (match := IMAGE_LINKS.match(attachment.url))
                )

            if match := IMAGE_LINKS.search(message.content):
                urls.append(match.group(1))
        return urls
