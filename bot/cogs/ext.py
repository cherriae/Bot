from __future__ import annotations

import discord
import re

from discord.ext import commands
from ..utils import Bot
from ..utils.helpers import Spotify


class ExtraCog(commands.Cog, command_attrs=dict(hidden=False)):
    hidden = False

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        self.lang_versions = {}


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

    @commands.command(name="spotify", aliases=["sp"], description="Return the user spotify activity")
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


    @commands.Cog.listener()
    async def on_message(self, message):
        messages = message.content
        messages = str(messages).replace(' ', '')

        if messages.startswith('user:'):
            _, user = messages.split(':')
            await message.channel.send(f"https://github.com/{user}")

        if messages.startswith('repo:'):
            _, repo = messages.split(':')
            await message.channel.send(f"https://github.com/{repo}")

    async def piston(self, language: str, code: str, version: str) -> dict:
        async with self.bot._session.post(
                "https://emkc.org/api/v2/piston/execute",
                json={
                    "language": language,
                    "version": version,
                    "files": [
                        {
                            "name": "main.py",
                            "content": code
                        }
                    ],
                    "compile_timeout": 10000,
                    "run_timeout": 3000,
                    "compile_memory_limit": -1,
                    "run_memory_limit": -1
                }
        ) as r:
            return await r.json()
        
    async def get_runtimes(self):
        async with self.bot._session as session:
            async with session.get("https://emkc.org/api/v2/piston/runtimes") as r:
                data = await r.json()
        for i in data:
            self.lang_versions[i['language']] = i['version']
            for alias in i['aliases']:
                self.lang_versions[alias] = i['version']
    

    @commands.command(name="runl", aliases=["p"], description="Run code single line")
    async def runl(self, ctx, language: str, *, codel: str):
        await self.get_runtimes()

        version = self.lang_versions.get(language)
        data = await self.piston(language, codel, version)

        output = data["run"]["output"]
        stderr = data["run"]["stderr"]
        stdout = data["run"]["stdout"]
        code = data["run"]["code"]
        signal = data["run"]["signal"]
        lang = data["language"]
        version = data["version"]

        embed = discord.Embed(
            title=f"{lang} {version}",
            description=f"```{lang}\n{output}```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="stdout", value=f"```{lang}\n{stdout}```", inline=True)
        embed.add_field(name="stderr", value=f"```{lang}\n{stderr}```", inline=True)
        embed.add_field(name="Signal/Code", value=f"`{signal}`/`{code}`", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="run", aliases=["r"], description="Run code")
    async def _run(self, ctx, *, code: str):
        matches = self.regex.findall(code)
        lang = lang = matches[0][0] or matches[0][1]
        code = matches[0][2]

        await self.get_runtimes()
        version = self.lang_versions.get(lang)

        data = await self.piston(lang, code, version)
        
        output = data["run"]["output"]
        stderr = data["run"]["stderr"]
        stdout = data["run"]["stdout"]
        code = data["run"]["code"]
        signal = data["run"]["signal"]
        lang = data["language"]
        version = data["version"]

        embed = discord.Embed(
            title=f"{lang} {version}",
            description=f"I ran your code! \n\n```{lang}\n{output}```",
            color=discord.Color.blurple()
        )
        embed.add_field(name="stdout", value=f"```{lang}\n{stdout}```", inline=True)
        embed.add_field(name="stderr", value=f"```{lang}\n{stderr}```", inline=True)
        embed.add_field(name="Signal/Code", value=f"`{signal}`/`{code}`", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="redo", aliases=["re"], description="Redo the last command (reply)")
    async def _redo(self, ctx):
        ref = ctx.message.reference
        if ref is None or ref.message_id is None:
            return
        try:
            message = await ctx.channel.fetch_message(ref.message_id)
        except Exception:
            return await ctx.reply("Couldn't find that message")
        if message.author != ctx.author:
            return
        await self.bot.process_commands(message)

async def setup(bot: Bot) -> None:
    await bot.add_cog(ExtraCog(bot))
