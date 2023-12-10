from __future__ import annotations

import discord
from discord.ext import commands
from typing import Optional

from ..utils import Bot, Tags


class TagCog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    
    @commands.group(name="tag", invoke_without_command=True, description="Tags")
    async def _tag(self, ctx, *, tag_name: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.get(tag_name)

        return await ctx.send(result)

    @_tag.command(name="create", description="Create a tag", aliases=["make"])
    async def _create(self, ctx, tag_name: str, *, tag_content: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.create(tag_name, tag_content)

        return await ctx.send(result)
    
    @_tag.command(name="delete", description="Delete a tag", aliases=["remove", 'rm'])
    async def _delete(self, ctx, tag_name: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.delete(tag_name)

        return await ctx.send(result)
    
    @_tag.command(name="raw", description="Get a tag without markdown")
    async def _raw(self, ctx, tag_name: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.get(tag_name)
        
        return await ctx.send(discord.utils.escape_markdown(result))
    
    @_tag.command(name="edit", description="Edit a value of tag", aliases=["change"])
    async def _edit(self, ctx, tag_name: str, *, new_content: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.edit(tag_name, new_content)

        return await ctx.send(result)
    
    @_tag.command(name="rename", description="Rename a tag name", aliases=["change_name"])
    async def _rename(self, ctx, tag_name: str, new_name: str):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.rename(tag_name, new_name)

        return await ctx.send(result)

    @_tag.command(name="alias", description="Give a tag an alias")
    async def _alias(self, ctx, tag_name, alias):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.add_alias(tag_name, alias)

        return await ctx.send(result)
    
    @_tag.command(name="delete_alias", description="Delete a tag's alias", aliases=["remove_alias", "rm_alias"])
    async def _delete_alias(self, ctx, tag_name, alias):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.delete_alias(tag_name, alias)

        return await ctx.send(result)

    @_tag.command(name="search", description="Search for a tag", aliases=["query", "find"])
    async def _search(self, ctx, *, query):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.query(query)

        return await ctx.send(result)
    
    @_tag.command(name="all", description="List all server tags", aliases=["list"])
    async def _all(self, ctx):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.list()

        return await ctx.send(result)
    
    @_tag.command(name="info", description="Get information on a tag", aliases=["about"])
    async def _info(self, ctx, tag_name):
        tag = Tags(ctx.guild.id, ctx.author.id)
        result = await tag.info(tag_name)

        return await ctx.send(result)
    
    @_tag.command(name="claim", description="Claim a tag if the author isn't in the server anymore")
    async def _claim(self, ctx, tag_name):
        tag = Tags(ctx.guild.id, ctx.author.id)
        owner = await tag.get_owner_id(tag_name)
        if ctx.guild.get_member(owner):
            return await ctx.send("Owner is still in this server")
        await tag.claim(tag_name, ctx.author.id)
        return await ctx.send("Claimed Tag")

    
    @commands.command(name="tags", description="Get all member's tags")
    async def _tags(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author

        tag = Tags(ctx.guild.id, member.id)
        result = await tag.author()

        return await ctx.send(result)


async def setup(bot: Bot):
    await bot.add_cog(TagCog(bot))
    