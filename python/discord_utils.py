import discord
from discord.ext.commands import Bot
import re


async def update_server_count(home_guild: discord.Guild, num_guilds: int):
    if home_guild is None:
        return
    name = f"Server Count: {num_guilds}"
    category_name = "BOT STATS"
    category = None
    for cat in home_guild.categories:
        if cat.name == category_name:
            category = cat
            break
    if category is None:
        category = await home_guild.create_category_channel(name=category_name)
        await home_guild.create_voice_channel(name=name, category=category, user_limit=0)
    else:
        channels = category.voice_channels
        edited = False
        for chan in channels:
            if chan.name.startswith("Server Count: "):
                try:
                    await chan.edit(name=name)
                    edited = True
                except:
                    pass
        if not edited:
            try:
                await home_guild.create_voice_channel(name=name, category=category, user_limit=0)
            except:
                pass


async def increment_command_count(bot: Bot, channel_id: int):
    match_string = r'(?P<desc>[a-zA-Z]*: )(?P<count>[0-9]*)'
    channel = bot.get_channel(channel_id)
    channel_name = channel.name
    match = re.search(match_string, channel_name)
    desc = match.group('desc')
    count = int(match.group('count')) + 1
    await channel.edit(name=f"{desc}{count}")
