from __future__ import annotations

# import logging

import discord
import datetime
import os
# import logging

from discord.ext import commands
from dotenv import load_dotenv
from typing import Optional
from aiohttp import ClientSession

# from .utils.help import CustomHelpCommand

load_dotenv()

__initial_extension__ = [
    "bot.cogs.ext",
    "bot.cogs.math"
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
            command_prefix=get_prefix,  # type: ignore
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
            case_sensitive=True,
            strip_after_prefix=True,
            # help_command = CustomHelpcommand
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
        await self._load_extensions()

    async def _load_extensions(self):
        self._extensions = __initial_extension__.copy() + __utils_extension__

        for extensions in self._extensions:
            try:
                await self.load_extension(extensions)  # type: ignore
            except Exception as e:
                raise e

    def run(self):
        super().run(token=os.getenv("TOKEN"), reconnect=True)
