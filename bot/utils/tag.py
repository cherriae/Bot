from __future__ import annotations

from ..db.database import TagModel
from typing import Union
from discord.utils import format_dt

class Tags:
    """
    A class representing a collection of tag-related operations.

    This class provides methods for retrieving, creating, deleting, editing, and managing tags.
    """
    def __init__(self, guild_id : int, author_id: int):
        self.guild_id = guild_id
        self.author_id = author_id

    async def get(self, name: str):
        """Retrieves the content of a tag by name.

        Args:
            name: The name of the tag to retrieve.

        Returns:
            str: The content of the tag if it exists, otherwise error message.

        """
        if tag := await TagModel.get_or_none(guild_id=self.guild_id, tag_name=name):
            await tag.update_from_dict({"uses": tag.uses + 1}).save()
            return tag.tag_content
        else:
            return "Tag Doesn't Exists"
        
    async def get_owner_id(self, tag_name) -> Union[int, str]:
        """Retrieves the ID of the owner of a tag.

        Args:
            tag_name: The name of the tag.

        Returns:
            Union[int, str]: The ID of the owner if the tag exists, otherwise an error message.

        """
        if tag := await TagModel.get_or_none(tag_name=tag_name, guild_id=self.guild_id):
            return tag.author_id
        else:
            return "Tag doesn't exists"


    async def create(self, name: str, content: str) -> str:
        """Creates a new tag with the specified name and content.

        Args:
            name: The name of the tag to create.
            content: The content of the tag.

        Returns:
            str: A message indicating the status of the tag creation.

        """
        if await TagModel.exists(guild_id=self.guild_id, tag_name=name):
            return "Tag already exists"
        await TagModel.create(guild_id=self.guild_id, tag_name=name, tag_content=content, author_id=self.author_id)
        return "Tag created"


    async def delete(self, name: str) -> str:
        """Deletes a tag with the specified name.

        Args:
            name: The name of the tag to delete.

        Returns:
            str: A message indicating the status of the tag deletion.

        """
        if not (
            tag := await TagModel.get_or_none(
                tag_name=name, guild_id=self.guild_id
            )
        ):
            return "Tag doesn't exists"
        if tag.author_id != self.author_id:
            return "You don't own this tag"
        if tag.aliases:
            await self.delete_alias(tag.tag_name, tag.aliases)
        await tag.delete()
        return "Tag deleted successfully"

    async def edit(self, name: str, content: str) -> str:
        """Edits the content of a tag with the specified name.

        Args:
            name: The name of the tag to edit.
            content: The new content of the tag.

        Returns:
            str: A message indicating the status of the tag editing.

        """
        if tag := await TagModel.get_or_none(tag_name=name, guild_id=self.guild_id):
            if tag.author_id == self.author_id:
                await tag.update_from_dict({"tag_content": content}).save()
                return "Tag edited"
            else:
                return "You don't own this tag"
        else:
            return "Tag doesn't exist"

    async def add_alias(self, tag_name: str, alias: str) -> str:
        """Adds an alias to a tag.

        Args:
            tag_name: The name of the tag to add an alias to.
            alias: The alias to add.

        Returns:
            str: A message indicating the status of the alias addition.

        """
        if not (
            tag := await TagModel.get_or_none(
                tag_name=tag_name, guild_id=self.guild_id
            )
        ):
            return "Tag doesn't exist"
        if tag.author_id != self.author_id:
            return "You don't own this tag"
        if await TagModel.exists(guild_id=self.guild_id, tag_name=alias):
            return "Can't add alias, name already exists"
        await TagModel.create(guild_id=self.guild_id, tag_name=alias, tag_content=tag.tag_content, author_id=self.author_id)
        await tag.update_from_dict({'aliases': alias}).save()
        return f"Added alias to `{tag_name}`, `{alias}`"

    async def delete_alias(self, tag_name: str, alias: str) -> str:
        """Deletes an alias from a tag.

        Args:
            tag_name: The name of the tag to delete an alias from.
            alias: The alias to delete.

        Returns:
            str: A message indicating the status of the alias deletion.

        """
        if tag := await TagModel.get_or_none(tag_name=tag_name, guild_id=self.guild_id):
            if tag.author_id == self.author_id:
                if tag_aliased := await TagModel.get_or_none(tag_name=alias, guild_id=self.guild_id):
                    await tag_aliased.delete()
                    await tag.update_from_dict({'aliases': None}).save()
                    return f"Deleted alias from `{tag_name}`"
                else:
                    return "Alias doesn't exist"
            else:
                return "You don't own this tag"
        else:
            return "Tag doesn't exist"

    async def rename(self, tag_name: str, new_name: str) -> str:
        """Renames a tag.

        Args:
            tag_name: The current name of the tag.
            new_name: The new name for the tag.

        Returns:
            str: A message indicating the status of the tag renaming.

        """
        if tag := await TagModel.get_or_none(tag_name=tag_name, guild_id=self.guild_id):
            if tag.author_id == self.author_id:
                if await TagModel.exists(guild_id=self.guild_id, tag_name=new_name):
                    return "Name already exists"
                await tag.update_from_dict({"tag_name": new_name}).save()
                return "Renamed tag"
            else:
                return "You don't own this tag"
        else:
            return "Tag doesn't exists"

    async def info(self, name: str) -> Union[dict, str]:
        """Retrieves information about a tag.

        Args:
            name: The name of the tag to retrieve information about.

        Returns:
            Union[dict, str]: A dictionary containing the tag information if the tag exists, otherwise an error message.

        """
        # get all information on the tag with {name}
        if tag := await TagModel.get_or_none(tag_name=name, guild_id=self.guild_id):
            tags = await TagModel.filter(guild_id=self.guild_id).order_by('-uses')

            return [
                tag.tag_name,
                tag.author_id,
                tag.uses,
                format_dt(tag.created_at),
                tag.aliases,
                next((index + 1 for index, t in enumerate(tags) if t.tag_name == tag.tag_name), None)
            ]
        else:
            return "Tag doesn't exists"

    async def list(self) -> Union[list, str]:
        """Lists all tags in the guild.

        Returns:
            Union[list, str]: A list of dictionaries representing the tags if there are any, otherwise an error message.

        """
        # list all tags in the guild
        if tags := await TagModel.filter(guild_id=self.guild_id):
            return "\n".join(
                f"{i+1}. `{name}`"
                for i, name in enumerate(
                    tag.tag_name for tag in tags
                )
            )
        if not tags:
            return "Server doesn't have any tags"

    async def query(self, query: str) -> Union[list, str]:
        """Queries for tags based on a search query.

        Args:
            query: The search query.

        Returns:
            Union[list, str]: A list of dictionaries representing the matching tags if there are any, otherwise an error message.

        """
        if tags := await TagModel.filter(guild_id=self.guild_id):
            return "\n".join(
                f"{i+1}. `{name}`"
                for i, name in enumerate(
                    tag.tag_name for tag in tags if query in tag.tag_name
                )
            )
        else:
            return "This server doesn't have any tags"

    async def author(self) -> Union[list, str]:
        """Retrieves all tags owned by the author.

        Returns:
            Union[list, str]: A list of dictionaries representing the tags if there are any, otherwise an error message.

        """
        if tags := await TagModel.filter(guild_id=self.guild_id, author_id=self.author_id):
            return "\n".join(
                    f"{i+1}. `{name}`"
                    for i, name in enumerate(
                        tag.tag_name for tag in tags
                    )
                )
        else:
            return "Member don't have any tags"

    async def claim(self, tag_name, new_author_id) -> str:
        """Claims ownership of a tag.

        Args:
            tag_name: The name of the tag to claim.
            new_author_id: The ID of the new owner.

        Returns:
            str: A message indicating the status of the ownership claim.

        """
        if tag := await TagModel.get_or_none(tag_name=tag_name, guild_id=self.guild_id):
            await tag.update_from_dict({"author_id": new_author_id}).save()
            return "Updated owner"
        else:
            return "Tag doesn't exists"
