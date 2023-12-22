from tortoise.models import Model
from tortoise import fields


class TagModel(Model):
    guild_id = fields.IntField()
    author_id = fields.IntField()
    tag_name = fields.TextField()
    tag_content = fields.TextField()
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    uses = fields.IntField(default=0)
    aliases = fields.TextField(null=True)

    def __str__(self):
        return self.tag_content

    class Meta:
        table = "Tags"

class LevelingSystem(Model):
    guild_id = fields.IntField()
    user_id = fields.IntField()
    xp = fields.IntField(default=0)
    xp_max = fields.IntField(default=100)
    level = fields.IntField(default=0)
    multiplier = fields.IntField(default=1)
    cooldown = fields.TextField(null=True)
    background_url = fields.TextField(null=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    
    class Meta:
        table = "Leveling System"

class LevelingSystemCard(Model):
    guild_id = fields.IntField()
    user_id = fields.IntField()
    background_url = fields.TextField(null=True)
    progress_bar_color = fields.TextField(default="#11ebf2")
    font_color = fields.TextField(default="#fff")

    class Meta:
        table = "Leveling System Card"
    