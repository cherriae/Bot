from __future__ import annotations

# import logging

import discord
import datetime
import os
# import logging

from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import ClientSession
from tortoise import Tortoise
from traceback import format_exception


# from .utils.help import CustomHelpCommand

load_dotenv()

__initial_extension__ = [
    "bot.cogs.ext",
    "bot.cogs.math",
    "bot.cogs.tags",
    "bot.cogs.leveling"
]

__utils_extension__ = [
    "jishaku",
    # "bot.cogs.handles"
]


def get_prefix(bot, message):
    prefixes = [">", "?", ".", "-", "coc!", "Coc!", "COc!", "COC!", "cOC!", "coc?", "Coc?", "COc?", "COC?", "cOC?", ]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name=">help"
            ),
            command_prefix=get_prefix,
            intents=discord.Intents(
                members=True,
                messages=True,
                message_content=True,
                guilds=True,
                bans=True,
            ),
            allowed_mentions=discord.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            case_sensitive=True,
            strip_after_prefix=True,
            auto_sync_commands=False,
            chunk_guilds_at_startup=False,
            help_command=None,
            #owner_ids=[YOUR_IDS_HERE], #integers only
            owner_id=int(os.getenv("OWNER_ID"))
        )

        self._launch_time = datetime.datetime.now(datetime.timezone.utc)

        # logging
        # logger = logging.getLogger('discord')
        # logger.setLevel(logging.DEBUG)
        # logging.getLogger('discord.http').setLevel(logging.INFO)
        # handler = logging.handlers.RotatingFileHandler(
        #   filename='discord.log',
        #   encoding='utf-8',
        #   maxBytes=32 * 1024 * 1024,  # 32 MiB
        #   backupCount=5,  # Rotate through 5 files
        # )
        # dt_fmt = '%Y-%m-%d %H:%M:%S'
        # formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)

    @property
    def _session(self):
        return ClientSession()

    async def on_ready(self):
        print("Bot is ready")

    async def _load_extensions(self):
        self._extensions = __initial_extension__.copy() + __utils_extension__

        for extensions in self._extensions:
            try:
                await self.load_extension(extensions)
            except Exception as e:
                raise e
            
    async def tortoise(self):
        await Tortoise.init(
            db_url="sqlite://bot/db/tortoise.db",
            modules={'models': ['bot.db.database']}
        )
        await Tortoise.generate_schemas()

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        await self.tortoise()
        await self._load_extensions()
        return await super().start(token, reconnect=reconnect)

    async def on_command_error(self, ctx, error):
        try:
            error = error.original
        except Exception:
            error = error

        if isinstance(error, commands.CommandNotFound):
            try:
                return await ctx.send("Command does not exist")

            except Exception:
                return

        
        owner = await self.fetch_user(self.owner_id)
        embed = discord.Embed(title=f"In Command: `{ctx.command.qualified_name}`", description=f"```py\n{''.join(format_exception(type(error), error, error.__traceback__))}```", colour=discord.Color.blurple())
        await owner.send(embed=embed)


    async def close(self) -> None:
        await Tortoise.close_connections()
        return await super().close()

    def run(self):
        super().run(token=os.getenv("TOKEN"))
