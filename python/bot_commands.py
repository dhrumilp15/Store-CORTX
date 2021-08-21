"""The core functionality of the bot."""
from search.async_search_client import AsyncSearchClient
from mongo_client import MgClient
from utils import filter_messages_with_permissions

import discord
from discord.ext import commands
from discord_slash import SlashContext
from typing import List, Dict


async def fremove(ctx: SlashContext or commands.Context,
                  filename: str,
                  search_client: AsyncSearchClient,
                  mg_client: MgClient,
                  bot: commands.Bot,
                  **kwargs) -> List[str]:
    """
    Remove files from search and database.

    Args:
        ctx: The message's origin
        filename: The query for files to remove
        search_client: The Search client
        mg_client: The MongoDB client
        bot: The discord bot

    Returns:
        A list of filenames that were deleted
    """
    author = ctx.author
    if not filename:
        return f"Couldn't process your query: `{filename}`"
    serv_id = ctx.channel.id
    if ctx.guild is not None:
        serv_id = ctx.guild.id

    files = await search_client.search(filename, serv_id, ctx.channel, **kwargs)

    manageable_files = filter_messages_with_permissions(
        author,
        files,
        discord.Permissions(read_message_history=True),
        bot
    )
    if not manageable_files:
        return f"I couldn't find any files related to `{filename}`"
    res = await search_client.remove_doc(
        [file['objectID'] for file in manageable_files],
        serv_id,
        author.name + "#" + author.discriminator
    )
    if not res.get('objectIDs'):
        return []
    res = await mg_client.remove_file([file['objectID'] for file in manageable_files])
    if not res:
        return []
    return manageable_files


async def fdelete(ctx: SlashContext or commands.Context, filename: str, search_client: AsyncSearchClient,
                  mg_client: MgClient, bot: commands.Bot, **kwargs) -> List[str]:
    """
    Remove files from our storage and delete their corresponding discord messages.

    Args:
        ctx: The message's origin
        filename: The query for files to remove
        search_client: The Search client
        mg_client: The MongoDB client
        bot: The discord bot

    Returns:
        A list of filenames that were deleted
    """
    author = ctx.author
    if not filename:
        return f"Couldn't process your query: `{filename}`"
    serv_id = ctx.channel.id
    if ctx.guild is not None:
        serv_id = ctx.guild.id
    files = await search_client.search(filename, serv_id, ctx.channel, **kwargs)
    manageable_files = filter_messages_with_permissions(
        author,
        files,
        discord.Permissions(read_message_history=True),
        bot
    )
    if not manageable_files:
        return f"I couldn't find any files related to `{filename}`"
    deleted_files = []
    await search_client.remove_doc(
        [file['objectID'] for file in manageable_files],
        serv_id,
        author.name + "#" + author.discriminator
    )
    await mg_client.remove_file([file['objectID'] for file in manageable_files])
    for file in manageable_files:
        try:
            onii_chan = bot.get_channel(int(file['channel_id']))
            message = await onii_chan.fetch_message(file['message_id'])
            await message.delete()
            deleted_files.append(file['file_name'])
        except (discord.Forbidden, discord.errors.NotFound):
            continue
    return deleted_files


async def fsearch(ctx: SlashContext or commands.Context,
                  filename: str,
                  search_client: AsyncSearchClient,
                  bot: commands.Bot,
                  **kwargs) -> List[Dict]:
    """
    Find docs related to a query in ElasticSearch.

    Args:
        ctx: The message's origin
        filename: The query
        search_client: The Search client
        bot: The discord bot

    Returns:
        A list of dicts of viewable files.
    """
    if not filename:
        return f"Couldn't process your query: `{filename}`"

    onii_chan = ctx.channel
    if ctx.guild is not None:
        onii_chan = ctx.guild

    files = await search_client.search(
        filename,
        onii_chan,
        ctx.channel,
        **kwargs
    )
    if not files:
        return f"I couldn't find any files related to your query"

    manageable_files = filter_messages_with_permissions(
        author=ctx.author,
        files=files,
        perm=discord.Permissions(read_message_history=True),
        bot=bot
    )
    if not manageable_files:
        return f"I couldn't find any files that you can access"
    return manageable_files
