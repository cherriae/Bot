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

