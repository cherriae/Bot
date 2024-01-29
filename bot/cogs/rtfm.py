from __future__ import annotations

import re
import discord
import aiohttp
from typing import Optional
from discord.ext import commands

from ..utils import WpilibRFTM, SphinxObjectFileReader, TARGETS, TARGETS_ALIASES


class RTFM(commands.Cog):
    url_overrides = {
        "tensorflow": "https://github.com/mr-ubik/tensorflow-intersphinx/raw/master/tf2_py_objects.inv"
    }

    def __init__(self, bot):
        self.bot = bot
        self._rtfm_cache = {}

    async def get_doc(self, docs: str):
        doc = TARGETS[docs]

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.http._HTTPClient__session  # type: ignore

    async def build(self, target) -> None:
        url = TARGETS[target]
        req = await self.session.get(
            self.url_overrides.get(target, f"{url}/objects.inv")
        )
        if req.status != 200:
            raise commands.CommandError("Failed to build RTFM cache")
        self._rtfm_cache[target] = SphinxObjectFileReader(
            await req.read()
        ).parse_object_inv(url)

    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        pat = ".*?".join(map(re.escape, str(text)))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            return (tup[0], tup[1], key(tup[2])) if key else tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    

    @commands.command(name="rtfm", aliases=["rtd"], description="")
    async def _rtfm(self, ctx, docs : str, *, query : Optional[str] = None):
        doc = docs.lower()

        target = None
        for aliases, target_name in TARGETS_ALIASES.items():
            if doc in aliases:
                target = target_name

        if docs.lower() == 'wpilib':
            if not query:
                return await ctx.send(WpilibRFTM("./bot/ext/json/wpilib.json").build())
            return await ctx.send(
                embed = discord.Embed(
                    title="Search in WPILIB",
                    description=str(WpilibRFTM("./bot/ext/json/wpilib.json").search_terms(query)),
                    color=discord.Color.dark_purple(),
                )
            )        

        if not target:
            return await ctx.reply("Alias/target not found")
        if not query:
            return await ctx.reply(TARGETS[target])

        cache = self._rtfm_cache.get(target)
        if not cache:
            await self.build(target)
            cache = self._rtfm_cache.get(target)

        if results := self.finder(
            query, list(cache.items()), key=lambda x: x[0], lazy=False
        )[:8]:
            await ctx.send(
                embed=discord.Embed(
                    title=f"Searched in {target}",
                    description="\n".join([f"[`{key}`]({url})" for key, url in results]),
                    color=discord.Color.dark_purple(),
                )
            )
        else:
            return await ctx.reply("Couldn't find any results")
        
async def setup(bot):
    await bot.add_cog(RTFM(bot))