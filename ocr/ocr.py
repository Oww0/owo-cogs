from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any, List

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box, pagify, pprint, text_to_file

from .converter import ImageFinder, find_images_in_replies, search_for_images
from .utils import vision_ocr as do_vision_ocr

if TYPE_CHECKING:
    from redbot.core.commands import Context
    from redbot.core.bot import Red

LOGGER = logging.getLogger("ocr.ocr")


class OCR(commands.Cog):
    """Detect text in images using ocr.space or Google Cloud Vision API."""

    __authors__ = ["<@306810730055729152>", "TrustyJAID"]
    __version__ = "2.3.2"

    def format_help_for_context(self, ctx: Context) -> str:
        """Thanks Sinbad."""
        return (
            f"{super().format_help_for_context(ctx)}\n\n"
            f"**Authors:**  {', '.join(self.__authors__)}\n"
            f"**Cog version:**  v{self.__version__}"
        )

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.ocr_ctx = discord.app_commands.ContextMenu(
            name="Run OCR",
            callback=self.ocr_ctx_menu,
        )
        self.ocr_translate_ctx = discord.app_commands.ContextMenu(
            name="OCR + Translate",
            callback=self.ocr_translate_ctx_menu,
        )

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.ocr_ctx)
        #  self.bot.tree.add_command(self.ocr_translate_ctx)
        return

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ocr_ctx.name, type=self.ocr_ctx.type)
        #  self.bot.tree.remove_command(self.ocr_translate_ctx.name, type=self.ocr_translate_ctx.type)
        return

    async def red_delete_data_for_user(self, **kwargs: Any) -> None:
        """Nothing to delete"""
        pass

    @staticmethod
    async def _pre_processing(inter: discord.Interaction[Red], message: discord.Message) -> str | None:
        LOGGER.debug(
            "%s (%s) used OCR ctx menu in %r in guild: %r (%s)",
            inter.user.name,
            inter.user.id,
            inter.channel,
            inter.guild,
            message.jump_url,
        )
        images = await find_images_in_replies(message)
        if not images:
            await inter.followup.send(
                "No images or image links were found in that message!",
                ephemeral=True,
            )
            return discord.utils.MISSING
        LOGGER.debug("\n".join(images))
        ctx = await commands.Context.from_interaction(inter)
        r = await do_vision_ocr(ctx, detect_handwriting=True, image=images[0])
        if not r:
            await inter.followup.send("OCR call failed guh :cry:", ephemeral=True)
            return discord.utils.MISSING
        return r.text_value

    async def ocr_ctx_menu(self, i: discord.Interaction[Red], message: discord.Message) -> None:
        hidden = True if message.guild else not i.app_permissions.send_messages
        if message.author.system or message.author.bot:
            hidden = False
            await i.response.send_message(
                file=text_to_file(pprint(message._data, sort_keys=False), 'message.json'),
                ephemeral=False,
            )
        if not i.response.is_done():
            await i.response.defer(ephemeral=hidden)
        text_value = await self._pre_processing(i, message)
        if text_value is discord.utils.MISSING:
            return
        if not text_value:
            await i.followup.send("No text content extracted from that image", ephemeral=hidden)
            return
        if len(text_value) > 1984:
            await i.followup.send(
                f"{i.user.mention} text output too long so attached as file:",
                file=text_to_file(text_value),
                ephemeral=hidden,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            await i.followup.send(box(text_value, "py"), ephemeral=hidden)
        return

    async def ocr_translate_ctx_menu(self, i: discord.Interaction[Red], message: discord.Message) -> None:
        hidden = True if message.guild else not i.app_permissions.send_messages
        await i.response.defer(ephemeral=hidden)
        text_value = await self._pre_processing(i, message)
        if text_value is discord.utils.MISSING:
            return
        if not text_value:
            await i.followup.send("No text content extracted from that image", ephemeral=True)
            return
        cog = i.client.get_cog("Translate")
        if not cog:
            await i.followup.send("Translate module not found wtf", ephemeral=True)
            return
        if TYPE_CHECKING:
            from translate.translate import Translate
            assert isinstance(cog, Translate)

        from translate.models import DetectedLanguage

        detected_lang = DetectedLanguage(language="auto", confidence=0)
        try:
            detected_lang = await cog._tr.detect_language(text_value, guild=i.guild)
        except Exception:
            from_lang = "auto"
        else:
            from_lang = detected_lang.language
        translated_text = await cog.run_translate(i, from_lang, "en", text_value)
        if not translated_text:
            if len(text_value) > 1984:
                await i.followup.send(file=text_to_file(text_value), ephemeral=True)
            else:
                await i.followup.send(box(text_value, "py"), ephemeral=True)
            return
        user = message.author
        _, embed = translated_text.embed(user, from_lang, "en", user, detected_lang.confidence)
        await i.followup.send(embed=embed, ephemeral=True)
        return

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(read_message_history=True)
    @commands.command()
    async def ocr(
        self,
        ctx: Context[Red],
        image: Annotated[List[str], ImageFinder] = None,
    ) -> None:
        """Detect text in an image through Google OCR API.

        Use it on old messages with attachments/image links by replying to said message with `[p]ocr`

        Pass `detect_handwriting` as True or `1` with command to more accurately detect handwriting from target image.

        **Example:**
        - `[p]ocr image/attachment/URL`
        - # To better detect handwriting in target image do:
        - `[p]ocr 1 image/attachment/URL`
        """
        await ctx.typing()
        if not image:
            attached = ctx.message.attachments
            mime_type = (attached[0].content_type if attached else None) or ""
            if attached and len(attached) == 1 and mime_type.startswith("image"):
                img = await attached[0].read(use_cached=True)
                r = await do_vision_ocr(ctx, image=img)
                if not r:
                    return
                await ctx.send_interactive(pagify(r.text_value or ""), box_lang="", timeout=120)
                return
            elif ctx.message.reference and (message := ctx.message.reference.resolved):
                image = await find_images_in_replies(message)
            else:
                image = await search_for_images(ctx)
            if not image:
                await ctx.send("No images or direct image links were detected. 😢")
                return
        resp = await do_vision_ocr(ctx, image=image[0])
        if not resp:
            return
        await ctx.send_interactive(pagify(resp.text_value or ""), box_lang="", timeout=120)
        return

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(read_message_history=True)
    @commands.command()
    async def ocrtr(
        self,
        ctx: Context[Red],
        image: Annotated[List[str], ImageFinder] = None,
    ) -> None:
        """Do OCR & translate on an image."""
        if not image:
            if ctx.message.reference and (message := ctx.message.reference.resolved):
                image = await find_images_in_replies(message)
            else:
                image = await search_for_images(ctx)
            if not image:
                await ctx.send("No images or direct image links were detected. 😢")
                return
        await ctx.typing()
        resp = await do_vision_ocr(ctx, image=image[0])
        if not resp:
            return

        text = resp.text_value or ""
        cog = ctx.bot.get_cog("Translate")
        if not cog:
            await ctx.send("Translate module not found nooooooo")
            return
        if TYPE_CHECKING:
            from translate.translate import Translate

            assert isinstance(cog, Translate)

        from translate.models import DetectedLanguage

        detected_lang = DetectedLanguage(language="auto", confidence=0)
        try:
            detected_lang = await cog._tr.detect_language(text, guild=ctx.guild)
        except Exception:
            # await ctx.send(str(exc))
            from_lang = ft.language_code if (ft := resp.fullTextAnnotation) else "auto"
        else:
            from_lang = detected_lang.language
        translated_text = await cog.run_translate(ctx, from_lang, "en", text)
        if not translated_text:
            await ctx.send_interactive(pagify(text), box_lang="", timeout=120)
            return
        _, embed = translated_text.embed(ctx.author, from_lang, "en", ctx.author, detected_lang.confidence)
        ref = ctx.message.to_reference(fail_if_not_exists=False)
        await ctx.send(embed=embed, reference=ref, mention_author=False)
        return

