from __future__ import annotations

import discord
import random

from discord.ext import commands
from ..utils import Leveling, RankCard, RankCardSetting

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="level", aliases=["lvl", "rank", "card"])
    async def _level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        leveling = await RankCard(guild_id=ctx.guild.id, author_id=member.id).generate(self.bot)
        if not leveling:
            return await ctx.send("User doesn't exist")
        await ctx.send(file=leveling)

    @_level.command(name="fontcolor", aliases=["fc"])
    async def _fontcolor(self, ctx, color: str = None): #hex code converter
        if not color:
            return await ctx.send("Please provide a color")
        await RankCardSetting(guild_id=ctx.guild.id, user_id=ctx.author.id).set_font_color(color)
        await ctx.send("Font color updated")

    @_level.command(name="progressbarcolor", aliases=["pbc"])
    async def _progressbarcolor(self, ctx, color: str = None): #hex code converter
        if not color:
            return await ctx.send("Please provide a color")
        await RankCardSetting(guild_id=ctx.guild.id, user_id=ctx.author.id).set_progress_bar_color(color)
        await ctx.send("Progress bar color updated")
    
    @_level.command(name="background", aliases=["bg"])
    async def _background(self, ctx, url: str = None):
        if not url:
            return await ctx.send("Please provide a url")
        await Leveling(ctx.guild.id, ctx.author.id).set_background(url)
        await ctx.send("Background updated")

    @commands.command(name="multiplier", aliases=["multi"])
    async def _multiplier(self, ctx, *, multiplier):
        if not multiplier:
            return await ctx.send("Please provide a multiplier")
        await Leveling(ctx.guild.id, ctx.author.id).set_multiplier(multiplier)
        await ctx.send("Multiplier updated")

    @commands.command(name="leaderboard", aliases=["lb"]) # TODO: make leaderboard card (image)
    async def _leaderboard(self, ctx):
        leaderboard = await Leveling(ctx.guild.id, ctx.author.id).leaderboard()
        
        embed = discord.Embed(title="Leaderboard", color=discord.Color.random())
        for key, user in leaderboard.items(): 
            embed.add_field(name=f"{int(key)}. {(await self.bot.fetch_user(user['user_id'])).name}", value=f"Level: {user['level']}", inline=False)
        await ctx.send(embed=embed) 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        await Leveling(guild_id=message.guild.id, author_id=message.author.id).add_xp(random.randint(1, 20))
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Leveling(guild_id=member.guild.id, author_id=member.id).create_user()
        await RankCardSetting(guild_id=member.guild.id, user_id=member.id).create_card()

async def setup(bot):
    await bot.add_cog(Level(bot))