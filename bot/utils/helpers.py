from __future__ import annotations

import discord
import asyncio
import functools
import datetime
import string


from discord import File
from discord.ext import commands
from io import BytesIO
from cbvx import iml
from PIL import Image, ImageDraw, ImageFont
from typing import Any, Callable, Tuple

from discord.ui import View


def executor() -> Callable[[Callable[..., Any]], Any]:
    def outer(func: Callable[..., Any]):
        @functools.wraps(func)
        def inner(*args: Any, **kwargs: Any):
            loop = asyncio.get_event_loop()
            thing = functools.partial(func, *args, **kwargs)
            return loop.run_in_executor(None, thing)

        return inner

    return outer


class Spotify:
    __slots__ = ("member", "bot", "embed", "regex", "headers", "counter")

    def __init__(self, *, bot, member) -> None:
        """
        Class that represents a Spotify object, used for creating listening embeds
        Parameters:
        ----------------
        bot : commands.Bot
            represents the Bot object
        member : discord.Member
            represents the Member object whose spotify listening is to be handled
        """
        self.member: discord.Member | discord.User = member
        self.bot: commands.Bot = bot
        self.counter = 0

    @staticmethod
    @executor()
    def pil_process(pic: BytesIO, name, artists, time, time_at, track) -> discord.File:
        """
        Makes an image with spotify album cover with Pillow

        Parameters:
        ----------------
        pic : BytesIO
            BytesIO object of the album cover
        name : str
            Name of the song
        artists : list
            Name(s) of the Artists
        time : int
            Total duration of song in xx:xx format
        time_at : int
            Total duration into the song in xx:xx format
        track : int
            Offset for covering the played bar portion
        Returns
        ----------------
        discord.File
            contains the spotify image
        """

        # Resize input image to 300x300
        d = Image.open(pic).resize((300, 300))
        # Save to a buffer as PNG
        buffer = BytesIO()
        d.save(buffer, "png")
        buffer.seek(0)
        # Pass raw bytes to cbvx.iml (needs to be png data)
        csp = iml.Spotify(buffer.getvalue())
        # Spotify class has 3 config methods - rate (logarithmic rate of interpolation),
        #  contrast, and shift (pallet shift)
        csp.rate(0.55)  # Higher = less sharp interpolation
        csp.contrast(20.0)  # default, Higher = more contrast
        csp.shift(0)  # default
        # _ is the bg color (non contrasted), we only care about foreground color
        _, fore = csp.pallet()
        fore = (fore.r, fore.g, fore.b)
        # We get the base to write text on
        result = csp.get_base()
        base = Image.frombytes("RGB", (600, 300), result)

        font0 = ImageFont.truetype("./bot/ext/fonts/spotify.ttf", 35)  # For title
        font2 = ImageFont.truetype("./bot/ext/fonts/spotify.ttf", 18)  # Time stamps

        draw = ImageDraw.Draw(
            base,
        )
        draw.rounded_rectangle(
            ((50, 230), (550, 230)),
            radius=1,
            fill=tuple(map(lambda c: int(c * 0.5), fore)),
        )  # play bar
        draw.rounded_rectangle(
            ((50, 230 - 1), (int(50 + track * 500), 230 + 1)),
            radius=1,
            fill=fore,
        )  # progress
        draw.ellipse(
            (int(50 + track * 500) - 5, 230 - 5, int(50 + track * 500) + 5, 230 + 5),
            fill=fore,
            outline=fore,
        )  # PlayReady
        draw.text((50, 245), time_at, fore, font=font2)  # Current time
        draw.text((500, 245), time, fore, font=font2)  # Total duration
        draw.text((50, 50), name, fore, font=font0)  # Track name
        draw.text((50, 100), artists, fore, font=font2)  # Artists

        output = BytesIO()
        base.save(output, "png")
        output.seek(0)
        return discord.File(fp=output, filename="spotify.png")

    async def get_from_local(self, bot, act: discord.Spotify) -> discord.File:
        """
        Makes an image with spotify album cover with Pillow

        Parameters:
        ----------------
        bot : commands.Bot
            represents our Bot object
        act : discord.Spotify
            activity object to get information from
        Returns
        ----------------
        discord.File
            contains the spotify image
        """
        s = tuple(f"{string.ascii_letters}{string.digits}{string.punctuation} ")
        artists = ", ".join(act.artists)
        artists = "".join([x for x in artists if x in s])
        artists = f"{artists[:36]}..." if len(artists) > 36 else artists
        time = act.duration.seconds
        time_at = (
            datetime.datetime.now(datetime.timezone.utc).replace(
                tzinfo=datetime.timezone.utc
            )
            - act.start
        ).total_seconds()
        track = time_at / time
        time = f"{time // 60:02d}:{time % 60:02d}"
        time_at = f"{int(max(time_at, 0) // 60):02d}:{int(max(time_at, 0) % 60):02d}"
        pog = act.album_cover_url
        name = "".join([x for x in act.title if x in s])
        name = f"{name[:21]}..." if len(name) > 21 else name
        rad = await bot._session.get(pog)
        pic = BytesIO(await rad.read())
        return await self.pil_process(pic, name, artists, time, time_at, track)

    async def get_embed(self) -> bool | Tuple[File, View]:
        """
        Creates the Embed object

        Returns
        ----------------
        Tuple[discord.Embed, discord.File]
            the embed object and the file with spotify image
        """
        activity = discord.utils.find(
            lambda activity: isinstance(activity, discord.Spotify),
            self.member.activities,
        )
        if not activity:
            return False
        url = activity.track_url
        image = await self.get_from_local(self.bot, activity)
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                url=url,
                style=discord.ButtonStyle.green,
                label="\u2007Open in Spotify",
                emoji="<:spotify:983984483755765790>",
            )
        )
        return image, view
