from tortoise.models import Model
from tortoise import fields


class Tags(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    value = fields.TextField()
    created = fields.DateField(auto_add_now=True)
    uses = fields.IntField()
    owner = fields.IntField()

    def __str__(self):
        return True
