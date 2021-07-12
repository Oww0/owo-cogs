from random import choice

import discord
from redbot.core import Config, commands
from redbot.core.commands import Context
from redbot.core.utils.chat_formatting import bold, quote

from .constants import *


class Roleplay(commands.Cog):
    """Do roleplay with your Discord friends or virtual strangers."""

    __author__ = "ow0x (<@306810730055729152>)"
    __version__ = "1.0.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nAuthor: {self.__author__}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 123456789987654321, force_registration=True)
        default_global = {"schema_version": 1}
        default_user = {
            "BAKA_SENT": 0,
            "BAKA_RECEIVED": 0,
            "BULLY_SENT": 0,
            "BULLY_RECEIVED": 0,
            "CUDDLE_SENT": 0,
            "CUDDLE_RECEIVED": 0,
            "CRY_COUNT": 0,
            "FEED_SENT": 0,
            "FEED_RECEIVED": 0,
            "HIGHFIVE_SENT": 0,
            "HIGHFIVE_RECEIVED": 0,
            "HUG_SENT": 0,
            "HUG_RECEIVED": 0,
            "KILL_SENT": 0,
            "KILL_RECEIVED": 0,
            "KISS_SENT": 0,
            "KISS_RECEIVED": 0,
            "LICK_SENT": 0,
            "LICK_RECEIVED": 0,
            "NOM_SENT": 0,
            "NOM_RECEIVED": 0,
            "PAT_SENT": 0,
            "PAT_RECEIVED": 0,
            "POKE_SENT": 0,
            "POKE_RECEIVED": 0,
            "PUNCH_SENT": 0,
            "PUNCH_RECEIVED": 0,
            "SLAP_SENT": 0,
            "SLAP_RECEIVED": 0,
            "SMUG_COUNT": 0,
            "TICKLE_SENT": 0,
            "TICKLE_RECEIVED": 0,
        }
        self.config.register_global(**default_global)
        self.config.register_member(**default_user)
        self.config.register_user(**default_user)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def baka(self, ctx: Context, *, member: discord.Member):
        """Call someone a BAKA with a GIF reaction!"""
        if member.id == ctx.me.id:
            return await ctx.send("**Ｎ Ｏ   Ｕ**")

        if member.id == ctx.author.id:
            return await ctx.send(f"{bold(ctx.author.name)}, you really are BAKA. Stupid!! 💩")

        await ctx.trigger_typing()
        baka_to = await self.config.member(ctx.author).BAKA_SENT()
        baka_from = await self.config.member(member).BAKA_RECEIVED()
        gbaka_to = await self.config.user(ctx.author).BAKA_SENT()
        gbaka_from = await self.config.user(member).BAKA_RECEIVED()
        await self.config.member(ctx.author).BAKA_SENT.set(baka_to + 1)
        await self.config.member(member).BAKA_RECEIVED.set(baka_from + 1)
        await self.config.user(ctx.author).BAKA_SENT.set(gbaka_to + 1)
        await self.config.user(member).BAKA_RECEIVED.set(gbaka_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = f"_**{ctx.author.name}** calls {member.mention} a BAKA bahahahahaha!!!_"
        embed.set_image(url=choice(BAKA))
        footer = (
            f"{ctx.author.name} used baka: {baka_to + 1} times so far.\n"
            + f"{member.name} got called a BAKA: {baka_from + 1} times  so far."
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def bully(self, ctx: Context, *, member: discord.Member):
        """Bully someone in this server with a funny GIF!"""
        if member.id == ctx.me.id:
            return await ctx.send("**Ｎ Ｏ   Ｕ**")

        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} Self bullying doesn't make sense. Stop it, get some help."
            )

        await ctx.trigger_typing()
        bully_to = await self.config.member(ctx.author).BULLY_SENT()
        bully_from = await self.config.member(member).BULLY_RECEIVED()
        gbully_to = await self.config.user(ctx.author).BULLY_SENT()
        gbully_from = await self.config.user(member).BULLY_RECEIVED()
        await self.config.member(ctx.author).BULLY_SENT.set(bully_to + 1)
        await self.config.member(member).BULLY_RECEIVED.set(bully_from + 1)
        await self.config.user(ctx.author).BULLY_SENT.set(gbully_to + 1)
        await self.config.user(member).BULLY_RECEIVED.set(gbully_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = f"_**{ctx.author.name}** bullies {member.mention}_ 🤡"
        embed.set_image(url=choice(BULLY))
        footer = (
            f"{ctx.author.name} bullied: {bully_to + 1} times so far.\n{member.name} "
            + f"got bullied: {bully_from + 1} times so far.\n"
            + f"Someone call police to get {ctx.author.name} arrested."
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def cry(self, ctx: Context):
        """Let others know that you feel like crying or just wanna cry."""
        await ctx.trigger_typing()
        cry_count = await self.config.member(ctx.author).CRY_COUNT()
        gcry_count = await self.config.user(ctx.author).CRY_COUNT()
        await self.config.member(ctx.author).CRY_COUNT.set(cry_count + 1)
        await self.config.user(ctx.author).CRY_COUNT.set(gcry_count + 1)
        embed = discord.Embed(colour=ctx.author.colour)
        embed.description = f"{ctx.author.mention} {choice(CRY_STRINGS)}"
        embed.set_image(url=choice(CRY))
        footer = f"{ctx.author.name} has cried {cry_count + 1} times in this server so far."
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def cuddle(self, ctx: Context, *, member: discord.Member):
        """Cuddle with a server member!"""
        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} According to all known laws of roleplay, "
                + "there is no way you can cuddle yourself! Go cuddle with "
                + "someone... or a pillow, if you're lonely like me. 😔"
            )

        await ctx.trigger_typing()
        cuddle_to = await self.config.member(ctx.author).CUDDLE_SENT()
        cuddle_from = await self.config.member(member).CUDDLE_RECEIVED()
        gcuddle_to = await self.config.user(ctx.author).CUDDLE_SENT()
        gcuddle_from = await self.config.user(member).CUDDLE_RECEIVED()
        await self.config.member(ctx.author).CUDDLE_SENT.set(cuddle_to + 1)
        await self.config.member(member).CUDDLE_RECEIVED.set(cuddle_from + 1)
        await self.config.user(ctx.author).CUDDLE_SENT.set(gcuddle_to + 1)
        await self.config.user(member).CUDDLE_RECEIVED.set(gcuddle_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = (
                f"Awww thanks for cuddles, {bold(ctx.author.name)}! Very kind of you. 😳"
            )
        else:
            message = f"_**{ctx.author.name}** cuddles_ {member.mention}"
        embed.set_image(url=str(choice(CUDDLE)))
        footer = (
            f"{ctx.author.name} sent: {cuddle_to + 1} cuddles so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {cuddle_from + 1} cuddles so far."
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def feed(self, ctx: Context, *, member: discord.Member):
        """Feed someone from this server virtually!"""
        if member.id == ctx.author.id:
            return await ctx.send(f"_{ctx.author.mention} eats {bold(choice(RECIPES))}!_")

        await ctx.trigger_typing()
        feed_to = await self.config.member(ctx.author).FEED_SENT()
        feed_from = await self.config.member(member).FEED_RECEIVED()
        gfeed_to = await self.config.user(ctx.author).FEED_SENT()
        gfeed_from = await self.config.user(member).FEED_RECEIVED()
        await self.config.member(ctx.author).FEED_SENT.set(feed_to + 1)
        await self.config.member(member).FEED_RECEIVED.set(feed_from + 1)
        await self.config.user(ctx.author).FEED_SENT.set(gfeed_to + 1)
        await self.config.user(member).FEED_RECEIVED.set(gfeed_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"OWO! Thanks for yummy food..., {bold(ctx.author.name)}! ❤️"
        else:
            message = f"_**{ctx.author.name}** feeds {member.mention} some delicious food!_"
        embed.set_image(url=choice(FEED))
        footer = (
            f"{ctx.author.name} have fed others: {feed_to + 1} times so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received some food: {feed_from + 1} times so far."
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def highfive(self, ctx: Context, *, member: discord.Member):
        """High-fives a user!"""
        if member.id == ctx.author.id:
            return await ctx.send(
                f"_{ctx.author.mention} high-fives themselves in mirror, I guess?_"
            )

        await ctx.trigger_typing()
        h5_to = await self.config.member(ctx.author).HIGHFIVE_SENT()
        h5_from = await self.config.member(member).HIGHFIVE_RECEIVED()
        gh5_to = await self.config.user(ctx.author).HIGHFIVE_SENT()
        gh5_from = await self.config.user(member).HIGHFIVE_RECEIVED()
        await self.config.member(ctx.author).HIGHFIVE_SENT.set(h5_to + 1)
        await self.config.member(member).HIGHFIVE_RECEIVED.set(h5_from + 1)
        await self.config.user(ctx.author).HIGHFIVE_SENT.set(gh5_to + 1)
        await self.config.user(member).HIGHFIVE_RECEIVED.set(gh5_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"_high-fives back to {bold(ctx.author.name)}_ 👀"
            embed.set_image(url="https://i.imgur.com/hQPCYUJ.gif")
        else:
            message = f"_**{ctx.author.name}** high fives_ {member.mention}"
            embed.set_image(url=choice(HIGHFIVE))
        footer = (
            f"{ctx.author.name} sent: {h5_to + 1} high-fives so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {h5_from + 1} high-fives so far."
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def hugs(self, ctx: Context, *, member: discord.Member):
        """Hug a user virtually on Discord!"""
        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} One dOEs NOt SiMplY hUg THeIR oWn sELF!!!!!"
            )

        await ctx.trigger_typing()
        hug_to = await self.config.member(ctx.author).HUG_SENT()
        hug_from = await self.config.member(member).HUG_RECEIVED()
        ghug_to = await self.config.user(ctx.author).HUG_SENT()
        ghug_from = await self.config.user(member).HUG_RECEIVED()
        await self.config.member(ctx.author).HUG_SENT.set(hug_to + 1)
        await self.config.member(member).HUG_RECEIVED.set(hug_from + 1)
        await self.config.user(ctx.author).HUG_SENT.set(ghug_to + 1)
        await self.config.user(member).HUG_RECEIVED.set(ghug_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"Awwww thanks! So nice of you! _hugs **{ctx.author.name}** back_ 🤗"
        else:
            message = f"_**{ctx.author.name}** hugs_ {member.mention} 🤗"
        embed.set_image(url=str(choice(HUG)))
        footer = (
            f"{ctx.author.name} gave: {hug_to + 1} hugs so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {hug_from + 1} hugs so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def kill(self, ctx: Context, *, member: discord.Member):
        """Virtually attempt to kill a server member with a GIF reaction!"""
        if member.id == ctx.me.id:
            return await ctx.send("**Ｎ Ｏ   Ｕ**")

        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} Seppukku is not allowed on my watch. 💀"
            )

        await ctx.trigger_typing()
        kill_to = await self.config.member(ctx.author).KILL_SENT()
        kill_from = await self.config.member(member).KILL_RECEIVED()
        gkill_to = await self.config.user(ctx.author).KILL_SENT()
        gkill_from = await self.config.user(member).KILL_RECEIVED()
        await self.config.member(ctx.author).KILL_SENT.set(kill_to + 1)
        await self.config.member(member).KILL_RECEIVED.set(kill_from + 1)
        await self.config.user(ctx.author).KILL_SENT.set(gkill_to + 1)
        await self.config.user(member).KILL_RECEIVED.set(gkill_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = f"_**{ctx.author.name}** tries to kill {member.mention}!_ 🇫"
        embed.set_image(url=choice(KILL))
        footer = (
            f"{ctx.author.name} attempted: {kill_to + 1} kills so far.\n"
            + f"{member.name} got killed: {kill_from + 1} times so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def kiss(self, ctx: Context, *, member: discord.Member):
        """[NSFW] Kiss a user! Only allowed in NSFW channel."""
        if not ctx.channel.is_nsfw():
            return await ctx.send("NSFW command blocked in non NSFW channel.")

        if member.id == ctx.author.id:
            return await ctx.send(
                f"Poggers {bold(ctx.author.name)}, you just kissed yourself! LOL!!! 💋"
            )

        await ctx.trigger_typing()
        kiss_to = await self.config.member(ctx.author).KISS_SENT()
        kiss_from = await self.config.member(member).KISS_RECEIVED()
        gkiss_to = await self.config.user(ctx.author).KISS_SENT()
        gkiss_from = await self.config.user(member).KISS_RECEIVED()
        await self.config.member(ctx.author).KISS_SENT.set(kiss_to + 1)
        await self.config.member(member).KISS_RECEIVED.set(kiss_from + 1)
        await self.config.user(ctx.author).KISS_SENT.set(gkiss_to + 1)
        await self.config.user(member).KISS_RECEIVED.set(gkiss_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"Awwww so nice of you! _kisses **{ctx.author.name}** back!_ 😘 🥰"
        else:
            message = f"_**{ctx.author.name}** kisses_ {member.mention} 😘 🥰"
        embed.set_image(url=str(choice(KISS)))
        footer = (
            f"{ctx.author.name} sent: {kiss_to + 1} kisses so far.\n"
            + f"{member.name} received: {kiss_from + 1} kisses so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def lick(self, ctx: Context, *, member: discord.Member):
        """[NSFW] Lick a user! Only allowed in NSFW channel."""
        if not ctx.channel.is_nsfw():
            return await ctx.send("NSFW command blocked in non NSFW channel.")

        if member.id == ctx.me.id:
            return await ctx.send(
                f"{ctx.author.mention} You wanna lick a bot? Very horny! Here, lick this: 🍆"
            )

        await ctx.trigger_typing()
        lick_to = await self.config.member(ctx.author).LICK_SENT()
        lick_from = await self.config.member(member).LICK_RECEIVED()
        glick_to = await self.config.user(ctx.author).LICK_SENT()
        glick_from = await self.config.user(member).LICK_RECEIVED()
        await self.config.member(ctx.author).LICK_SENT.set(lick_to + 1)
        await self.config.member(member).LICK_RECEIVED.set(lick_from + 1)
        await self.config.user(ctx.author).LICK_SENT.set(glick_to + 1)
        await self.config.user(member).LICK_RECEIVED.set(glick_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = (
            f"{ctx.author.mention} Poggers, you just licked yourself. 👏"
            if member.id == ctx.author.id
            else f"_**{ctx.author.name}** licks_ {member.mention} 😳"
        )
        embed.set_image(url=choice(LICK))
        footer = (
            f"{ctx.author.name} have licked others: {lick_to + 1} times so far.\n"
            + f"{member.name} got licked: {lick_from + 1} times so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def nom(self, ctx: Context, *, member: discord.Member):
        """Try to nom/bite a server member!"""
        if member.id == ctx.me.id:
            return await ctx.send(f"**OH NO!** _runs away_")

        message = (
            f"Waaaaaa! {bold(ctx.author.name)}, You bit yourself! Whyyyy?? 😭"
            if member.id == ctx.author.id
            else f"_**{ctx.author.name}** casually noms_ {member.mention} 😈"
        )
        await ctx.trigger_typing()
        nom_to = await self.config.member(ctx.author).NOM_SENT()
        nom_from = await self.config.member(member).NOM_RECEIVED()
        gnom_to = await self.config.user(ctx.author).NOM_SENT()
        gnom_from = await self.config.user(member).NOM_RECEIVED()
        await self.config.member(ctx.author).NOM_SENT.set(nom_to + 1)
        await self.config.member(member).NOM_RECEIVED.set(nom_from + 1)
        await self.config.user(ctx.author).NOM_SENT.set(gnom_to + 1)
        await self.config.user(member).NOM_RECEIVED.set(gnom_from + 1)
        embed = discord.Embed(colour=member.colour)
        embed.set_image(url=choice(BITE))
        footer = (
            f"{ctx.author.name} nom'd: {nom_to + 1} times so far.\n"
            + f"{member.name} received: {nom_from + 1} noms so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def pat(self, ctx: Context, *, member: discord.Member):
        """Pat a server member with wholesome GIF!"""
        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} _pats themselves, I guess? **yay**_ 🎉"
            )

        await ctx.trigger_typing()
        pat_to = await self.config.member(ctx.author).PAT_SENT()
        pat_from = await self.config.member(member).PAT_RECEIVED()
        gpat_to = await self.config.user(ctx.author).PAT_SENT()
        gpat_from = await self.config.user(member).PAT_RECEIVED()
        await self.config.member(ctx.author).PAT_SENT.set(pat_to + 1)
        await self.config.member(member).PAT_RECEIVED.set(pat_from + 1)
        await self.config.user(ctx.author).PAT_SENT.set(gpat_to + 1)
        await self.config.user(member).PAT_RECEIVED.set(gpat_from + 1)
        message = (
            f"Wowie! Thanks {bold(ctx.author.name)} for giving me pats. 😳 😘"
            if member.id == ctx.me.id
            else f"_**{ctx.author.name}** pats_ {member.mention}"
        )
        embed = discord.Embed(colour=member.colour)
        embed.set_image(url=choice(PAT))
        footer = (
            f"{ctx.author.name} gave: {pat_to + 1} pats so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {pat_from + 1} pats so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def poke(self, ctx: Context, *, member: discord.Member):
        """Poke your Discord friends or strangers!"""
        if member.id == ctx.author.id:
            return await ctx.send(f"{bold(ctx.author.name)} wants to play self poke huh?!")

        await ctx.trigger_typing()
        poke_to = await self.config.member(ctx.author).POKE_SENT()
        poke_from = await self.config.member(member).POKE_RECEIVED()
        gpoke_to = await self.config.user(ctx.author).POKE_SENT()
        gpoke_from = await self.config.user(member).POKE_RECEIVED()
        await self.config.member(ctx.author).POKE_SENT.set(poke_to + 1)
        await self.config.member(member).POKE_RECEIVED.set(poke_from + 1)
        await self.config.user(ctx.author).POKE_SENT.set(gpoke_to + 1)
        await self.config.user(member).POKE_RECEIVED.set(gpoke_from + 1)
        embed = discord.Embed(colour=member.colour)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"Awwww! Hey there. _pokes **{ctx.author.name}** back!_"
        else:
            message = f"_**{ctx.author.name}** casually pokes_ {member.mention}"
        embed.set_image(url=choice(POKE))
        footer = (
            f"{ctx.author.name} gave: {poke_to + 1} pokes so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {poke_from + 1} pokes so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def punch(self, ctx: Context, *, member: discord.Member):
        """Punch someone on Discord with a GIF reaction!"""
        if member.id == ctx.me.id:
            message = (
                f"{ctx.author.mention} tried to punch a bot but failed miserably,\n"
                + "and they actually punched themselves instead.\n"
                + "How disappointing LMFAO! 😂 😂 😂"
            )
            em = discord.Embed(colour=await ctx.embed_colour())
            em.set_image(url="https://i.imgur.com/iVgOijZ.gif")
            return await ctx.send(content=message, embed=em)

        if member.id == ctx.author.id:
            return await ctx.send(
                f"I uh ..... **{ctx.author.name}**, self harm doesn't"
                + " sound so fun. Stop it, get some help."
            )

        await ctx.trigger_typing()
        punch_to = await self.config.member(ctx.author).PUNCH_SENT()
        punch_from = await self.config.member(member).PUNCH_RECEIVED()
        gpunch_to = await self.config.user(ctx.author).PUNCH_SENT()
        gpunch_from = await self.config.user(member).PUNCH_RECEIVED()
        await self.config.member(ctx.author).PUNCH_SENT.set(punch_to + 1)
        await self.config.member(member).PUNCH_RECEIVED.set(punch_from + 1)
        await self.config.user(ctx.author).PUNCH_SENT.set(gpunch_to + 1)
        await self.config.user(member).PUNCH_RECEIVED.set(gpunch_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = f"_**{ctx.author.name}** {choice(PUNCH_STRINGS)}_ {member.mention}"
        embed.set_image(url=choice(PUNCH))
        footer = (
            f"{ctx.author.name} sent: {punch_to + 1} punches so far.\n"
            + f"{member.name} received: {punch_from + 1} punches so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def slap(self, ctx: Context, *, member: discord.Member):
        """Slap a server member!"""
        if member.id == ctx.me.id:
            return await ctx.send("**Ｎ Ｏ   Ｕ**")

        if member.id == ctx.author.id:
            return await ctx.send(f"{ctx.author.mention} Don't slap yourself, you're precious!")

        await ctx.trigger_typing()
        slap_to = await self.config.member(ctx.author).SLAP_SENT()
        slap_from = await self.config.member(member).SLAP_RECEIVED()
        gslap_to = await self.config.user(ctx.author).SLAP_SENT()
        gslap_from = await self.config.user(member).SLAP_RECEIVED()
        await self.config.member(ctx.author).SLAP_SENT.set(slap_to + 1)
        await self.config.member(member).SLAP_RECEIVED.set(slap_from + 1)
        await self.config.user(ctx.author).SLAP_SENT.set(gslap_to + 1)
        await self.config.user(member).SLAP_RECEIVED.set(gslap_from + 1)
        embed = discord.Embed(colour=member.colour)
        message = f"_**{ctx.author.name}** slaps_ {member.mention}"
        embed.set_image(url=choice(SLAP))
        footer = (
            f"{ctx.author.name} gave: {slap_to + 1} slaps so far.\n"
            + f"{member.name} received: {slap_from + 1} slaps so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def smug(self, ctx: Context):
        """Show everyone your smug face!"""
        message = f"_**{ctx.author.name}** smugs at **@\u200bsomeone**_ 😏"
        await ctx.trigger_typing()
        smug_count = await self.config.member(ctx.author).SMUG_COUNT()
        gsmug_count = await self.config.user(ctx.author).SMUG_COUNT()
        await self.config.member(ctx.author).SMUG_COUNT.set(smug_count + 1)
        await self.config.user(ctx.author).SMUG_COUNT.set(gsmug_count + 1)
        embed = discord.Embed(colour=ctx.author.colour)
        embed.set_image(url=choice(SMUG))
        footer = f"{ctx.author.name} has smugged {smug_count + 1} times in this server so far."
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def tickle(self, ctx: Context, *, member: discord.Member):
        """Try to tickle a server member!"""
        if member.id == ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} tickling yourself is boring!"
                + " Tickling others is more fun though, right? 😏"
            )

        await ctx.trigger_typing()
        tickle_to = await self.config.member(ctx.author).TICKLE_SENT()
        tickle_from = await self.config.member(member).TICKLE_RECEIVED()
        gtickle_to = await self.config.user(ctx.author).TICKLE_SENT()
        gtickle_from = await self.config.user(member).TICKLE_RECEIVED()
        await self.config.member(ctx.author).TICKLE_SENT.set(tickle_to + 1)
        await self.config.member(member).TICKLE_RECEIVED.set(tickle_from + 1)
        await self.config.user(ctx.author).TICKLE_SENT.set(gtickle_to + 1)
        await self.config.user(member).TICKLE_RECEIVED.set(gtickle_from + 1)
        embed = discord.Embed(colour=member.colour)
        if member.id == ctx.me.id:
            message = f"_Wow, nice tickling skills, {bold(ctx.author.name)}. I LOL'd._ 🤣 🤡"
            embed.set_image(url="https://i.imgur.com/6jr50Fp.gif")
        else:
            message = f"_**{ctx.author.name}** tickles_ {member.mention}"
            embed.set_image(url=choice(TICKLE))
        footer = (
            f"{ctx.author.name} tickled others: {tickle_to + 1} times so far.\n"
            + f"{'I' if member == ctx.me else member.name} "
            + f"received: {tickle_from + 1} tickles so far!"
        )
        embed.set_footer(text=footer)

        await ctx.send(content=quote(message), embed=embed)
