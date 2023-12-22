from __future__ import annotations

import aiohttp
import io
import discord

from PIL import Image, ImageDraw, ImageFont
from typing import Union, Optional
from ..db.database import LevelingSystem, LevelingSystemCard
from datetime import datetime

class RankCardSetting:
    def __init__(self, guild_id: int, user_id: int) -> None:
        self.guild_id = guild_id
        self.user_id = user_id
        self.session = aiohttp.ClientSession()
    
    async def create_card(self) -> Union[bool, str]:
        if await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            return "User already exists"
        await LevelingSystemCard.create(
            guild_id=self.guild_id,
            user_id=self.user_id,
            background_url=None,
            progress_bar_color="#11ebf2",
            font_color="#fff"
        )
        return True


    async def fetch_background_image(self, background_url: str) -> io.BytesIO:
        async with self.session as session:
            async with session.get(background_url) as resp:
                return io.BytesIO(await resp.read())

    async def get_background_image(self) -> io.BytesIO:
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            if user.background_url:
                return Image.open(await self.fetch_background_image(user.background_url)).resize((1000, 240))
            else:
                return Image.open('./bot/ext/images/background.jpg').resize((1000, 240))
        else:
            return False  

    async def set_background(self, background_url: str = None) -> Union[bool, str]:
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            await user.update_from_dict({"background_url": background_url or None}).save()
            return True
        else:
            return "User doesn't exists"   
    
    async def progress_bar_color(self):
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            return user.progress_bar_color
        else:
            return False
    
    async def set_progress_bar_color(self, color: str = None) -> Union[bool, str]:
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            await user.update_from_dict({"progress_bar_color": color or "#11ebf2"}).save()
            return True
        else:
            return "User doesn't exists"
        
    async def font_color(self):
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            return user.font_color
        else:
            return False
    
    async def set_font_color(self, font_color: str = None) -> Union[bool, str]:
        if user := await LevelingSystemCard.get_or_none(guild_id=self.guild_id, user_id=self.user_id):
            await user.update_from_dict({"font_color": font_color or "#fff"}).save()
            return True
        else:
            return "User doesn't exists"

class Leveling:
    def __init__(self, guild_id: int, author_id: int) -> None:
        self.guild_id = guild_id
        self.author_id = author_id
            
    async def get_user(self) -> Union[LevelingSystem, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return user
        else:
            return False
        
        
    async def add_xp(self, xp: int) -> Union[bool, str]:
        if not (
            user := await LevelingSystem.get_or_none(
                guild_id=self.guild_id, user_id=self.author_id
            )
        ):
            await self.create_user()
            await RankCardSetting(guild_id=self.guild_id, user_id=self.author_id).create_card()
            return True
            
        cooldown_time = datetime.strptime(str(user.cooldown), "%Y-%m-%d %H:%M:%S.%f")
        time_difference = datetime.now() - cooldown_time

        if time_difference.total_seconds() < 15:
            return False
        
        accumulated_xp = (user.xp) + (xp * user.multiplier)
        xp_max = user.xp_max
        level = user.level

        while accumulated_xp >= xp_max:
            levels = int(accumulated_xp / user.xp_max)
            accumulated_xp -= user.xp_max * levels
            xp_max += 100 * levels
            level += levels

        await user.update_from_dict({"xp": accumulated_xp, "xp_max": xp_max, "level": level, "cooldown": str(datetime.now())}).save()
        return True
        
    async def create_user(self) -> Union[bool, str]:
        if await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return "User already exists"
        await LevelingSystem.create(
            guild_id=self.guild_id,
            user_id=self.author_id,
            xp=0,
            xp_max=100,
            level=1,
            multiplier=1,
            cooldown=datetime.now()
        )
        return True
        
    async def delete_user(self) -> Union[bool, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            await user.delete()
            return True
        else:
            return "User doesn't exists"
    
    async def get_time_created(self) -> str:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return str(user.created_at)
        else:
            return "User doesn't exists"

    async def get_xp(self) -> Union[int, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return user.xp
        else:
            return "User doesn't exists"
        
    async def get_max_xp(self) -> Union[int, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return user.xp_max
        else:
            return "User doesn't exists"
        
    async def get_level(self) -> Union[int, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return user.level
        else:
            return "User doesn't exists"
    
    async def get_multiplier(self) -> Union[int, str]:
        if user := await LevelingSystem.get_or_none(guild_id=self.guild_id, user_id=self.author_id):
            return user.multiplier
        else:
            return "User doesn't exists"
        
    async def set_multiplier(self, multiplier: int) -> Union[bool, str]:
        if not (
            user := await LevelingSystem.get_or_none(
                guild_id=self.guild_id, user_id=self.author_id
            )
        ):

            return "User doesn't exists"
        await user.update_from_dict({"multiplier": multiplier}).save()
        return True


        
    async def get_rank(self):
        if await LevelingSystem.get_or_none(guild_id=self.guild_id):
            users = await LevelingSystem.filter(guild_id=self.guild_id).order_by("-level")
            return next((index + 1 for index, u in enumerate(users) if u.user_id == self.author_id), None)
        else:
            return "Guild doesn't exists"
        
    async def leaderboard(self):
        if users := await LevelingSystem.filter(guild_id=self.guild_id).order_by("-level").limit(10):
            # return a dictionary like {"1": {"user_id": 123, "level": 1}, "2": {"user_id": 123, "level": 1}}
            return {str(i+1): {"user_id": user.user_id, "level": user.level} for i, user in enumerate(users)}
        else:
            return "Guild doesn't exists"
        
class RankCard:
    def __init__(self, guild_id: int, author_id: int):
        self.guild_id = guild_id
        self.author_id = author_id
        self.system = Leveling(self.guild_id, self.author_id)
        self.session = aiohttp.ClientSession()
        self.get_fonts

    async def colors(self):
        self.progress_bar_color = await RankCardSetting(self.guild_id, self.author_id).progress_bar_color()
        self.font_color = await RankCardSetting(self.guild_id, self.author_id).font_color()
              
    async def get_avatar(self, bot) -> io.BytesIO:
        async with self.session as session:
            user = await bot.fetch_user(self.system.author_id)
            avatar_url = user.avatar.url
            async with session.get(str(avatar_url)) as resp:
                return io.BytesIO(await resp.read())



    async def background(self):
        await self.colors()
        self.background = await RankCardSetting(self.guild_id, self.author_id).get_background_image()
            
    async def avatar(self, bot):
        self.avatar = Image.open(await self.get_avatar(bot)).resize((200, 200))

    async def apply_mask(self) -> None:

        bigsize = (int(self.avatar.size[0]) * 3, int(self.avatar.size[1]) * 3)
        mask = Image.new('L', bigsize, 0)

        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)

        mask = mask.resize(self.avatar.size, Image.Resampling.LANCZOS)
        self.avatar.putalpha(mask)

        self.background.paste(self.avatar, (20, 20), mask=self.avatar)

        self.draw = ImageDraw.Draw(self.background, 'RGB')

    @property
    def get_fonts(self):
        self.big_font = ImageFont.FreeTypeFont('./bot/ext/fonts/ABeeZee-Regular.otf', 60)
        self.medium_font = ImageFont.FreeTypeFont('./bot/ext/fonts/ABeeZee-Regular.otf', 40)
        self.small_font = ImageFont.FreeTypeFont('./bot/ext/fonts/ABeeZee-Regular.otf', 30)
        self.bigger_small_font = ImageFont.FreeTypeFont('./bot/ext/fonts/ABeeZee-Regular.otf', 35)
        self.smaller_font = ImageFont.FreeTypeFont('./bot/ext/fonts/ABeeZee-Regular.otf', 15)
        self.other_font =  ImageFont.FreeTypeFont('./bot/ext/fonts/SourceSansPro-Black.otf', 40)

    async def level_text(self):
        text_offset_x = self.bar_offset_x + 250
        text_offset_y = 183.328125 - 65.5
        self.draw1.text((text_offset_x, text_offset_y), f"Level: {await self.system.get_level()}", font=self.bigger_small_font, fill=self.font_color)

    async def progress_bar(self):
        self.draw1 = ImageDraw.Draw(self.background)

        self.bar_offset_x = int(self.avatar.size[0]) + 40 + 20
        self.bar_offset_y = 160
        self.bar_offset_x_1 = 1000 - 50
        self.bar_offset_y_1 = 200

        circle_size = self.bar_offset_y_1 - self.bar_offset_y
        self.draw1.rectangle((self.bar_offset_x, self.bar_offset_y, self.bar_offset_x_1, self.bar_offset_y_1), fill="#727175")
        self.draw1.ellipse((self.bar_offset_x - circle_size//2, self.bar_offset_y, self.bar_offset_x + circle_size//2, self.bar_offset_y + circle_size), fill="#727175")
        self.draw1.ellipse((self.bar_offset_x_1 - circle_size//2, self.bar_offset_y, self.bar_offset_x_1 + circle_size//2, self.bar_offset_y_1), fill="#727175")

        bar_length = self.bar_offset_x_1 - self.bar_offset_x
        progress = (int(await self.system.get_max_xp()) - int(await self.system.get_xp())) * 100/int(await self.system.get_max_xp())
        progress = 100 - progress
        progress_bar_length = round(bar_length * progress / 100)
        pbar_offset_x_1 = self.bar_offset_x + progress_bar_length
        self.draw1.rectangle((self.bar_offset_x, self.bar_offset_y, pbar_offset_x_1, self.bar_offset_y_1), fill=self.progress_bar_color)
        self.draw1.ellipse((self.bar_offset_x - circle_size//2, self.bar_offset_y, self.bar_offset_x + circle_size//2, self.bar_offset_y + circle_size), fill=self.progress_bar_color)
        self.draw1.ellipse((pbar_offset_x_1 - circle_size//2, self.bar_offset_y, pbar_offset_x_1 + circle_size//2, self.bar_offset_y_1), fill=self.progress_bar_color)
        percentage_text = f"{int(100 / int(await self.system.get_max_xp()) * int(await self.system.get_xp()))}%"
        text_offset_x = 245
        text_offset_y = 183.328125 - 65.5
        self.draw1.text((text_offset_x, text_offset_y), percentage_text, font=self.bigger_small_font, fill=self.font_color)

    async def member_and_rank_text(self, member: discord.Member):
        member_name_text = f"{member.display_name}"
        rank = await self.system.get_rank()

        # Calculate text size for member name text
        text_size_name = self.draw1.textlength(member_name_text, font=self.medium_font)

        # Set initial offset for member name text
        text_offset_x_name = self.bar_offset_x - 20
        text_offset_y_name = self.bar_offset_y - int(text_size_name) - 50

        # Draw member name text
        self.draw1.text((text_offset_x_name, text_offset_y_name), member_name_text, font=self.medium_font, fill=self.font_color)
    
        # Set the offset_x for the rank text to be at the end of the member name text
        text_offset_x_label = text_offset_x_name + text_size_name + 440
        offset_y = self.bar_offset_y - int(text_size_name) - 60

        self.draw.text((text_offset_x_label, offset_y+12), "Rank:", font=self.medium_font, fill=self.font_color)

        # Set the common offset_y for both rank and member name text

        # Draw the rank text
        self.draw.text((text_offset_x_name + text_size_name + 550, offset_y), f"#{rank}", font=self.big_font, fill=self.font_color)



    async def xp_text(self):
        xp_text = f"XP: {await self.system.get_xp()}/{await self.system.get_max_xp()}"
        text_offset_x = 750
        text_offset_y = 183.328125 - 65.5
        self.draw1.text((text_offset_x, text_offset_y), xp_text, font=self.bigger_small_font, fill=self.font_color)
        


    async def generate(self, bot):
        await self.background()
        await self.avatar(bot)
        await self.apply_mask()
        await self.progress_bar()
        await self.member_and_rank_text(await bot.fetch_user(self.author_id))
        await self.xp_text()
        await self.level_text()
        
        Imagebytes = io.BytesIO()
        self.background.save(Imagebytes, 'JPEG')
        Imagebytes.seek(0)
        return discord.File(fp=Imagebytes, filename=f"rank_card_{self.author_id}.jpg")

