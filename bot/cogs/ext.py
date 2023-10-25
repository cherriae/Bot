from __future__ import annotations

import discord

from discord.ext import commands
from ..utils import Bot
from ..utils.helpers import Spotify


class ExtraCog(commands.Cog, command_attrs=dict(hidden=False)):
    hidden = False

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.group(name="avatar", aliases=["pfp", "profile"], description="Shows the target display profile picture",
                    invoke_without_command=True)
    async def _avatar(self, ctx: commands.Context[Bot], *, member: commands.MemberConverter = None):
        member = ctx.author if member is None else member
        embed = (
            (
                discord.Embed(
                    title=f"Display Avatar of {member.display_name}",
                    color=discord.Colour.blurple()
                )
                .set_image(url=member.display_avatar.url))
            .set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        )
        await ctx.send(embed=embed)

    @_avatar.command(name="main", description="Shows the target main profile picture")
    async def _main(self, ctx: commands.Context[Bot], *, member: commands.MemberConverter = None):
        member = ctx.author if member is None else member
        embed = (
            (
                discord.Embed(
                    title=f"Main Avatar of {member.display_name}",
                    color=discord.Colour.blurple()
                )
                .set_image(url=member.avatar.url))
            .set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

        )
        await ctx.send(embed=embed)

    @commands.command(name="spotify", aliases=["sp"])
    @commands.cooldown(5, 60, type=commands.BucketType.user)
    async def _spotify(self, ctx, member: commands.MemberConverter = None):
        member = ctx.author if member is None else member

        spotify = Spotify(bot=self.bot, member=member)
        listening_to = await spotify.get_embed()

        if listening_to:
            file, view = listening_to
            return await ctx.send(file=file, view=view)

        return await ctx.reply(
            f"{member} are currently not listening to spotify!", mention_author=False
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(ExtraCog(bot))
