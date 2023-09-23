from datetime import datetime
from typing import List, Optional
import time as tea_time

import discord
from discord import app_commands
from discord.ext import commands
import psutil

from .help import MyHelpCommand

from constants import DIAMOND, DESCRIPTION, STARTTIME

import os
import platform
import re
import subprocess
import psutil
from pathlib import Path
from discord import __version__ as dpy_version


class Meta(commands.Cog, name='meta'):
    """Meta commands."""
    COG_EMOJI = '🏛'

    def __init__(self, bot: discord.Client):
        self.bot:discord.Client = bot

        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.hybrid_command(aliases=['uptime', 'botInfo', 'status','info'])
    @commands.cooldown(1, 3, commands.BucketType.default)
    async def about(self, ctx:commands.Context):
        """Shows info about this bot and the project."""
        async with ctx.typing():
            embed = discord.Embed(
                title=f'About {self.bot.user.name}',
                description=f'{DESCRIPTION if DESCRIPTION!=""else"..."}\n'\
                    +f'Use `{ctx.clean_prefix}help` for a list of commands.\n',
                colour = 0xa69f9c
            )
            
            # what this is doing is subtracting the date from the bot initialised date
            # and displaying it as the uptime in days.
            unformatted_uptime = abs(datetime.utcnow() - STARTTIME)
            days = unformatted_uptime.days
            hours = unformatted_uptime.seconds//3600
            days = f'{days} day{"" if days == 1 else "s"}'
            hours = f'{hours} hour{"" if hours == 1 else "s"}'

            try:
                bmem = f'{psutil.Process().memory_info().rss/1000000:.2f}'
                bstore = f'{sum(f.stat().st_size for f in Path(".").glob("**/*") if f.is_file())/1024/1024:.2f}'
            except Exception as e:
                bmem = '?'
                bstore = '?'
            
            bot_info=\
            f'{DIAMOND} Uptime: `{days}`, `{hours}`'\
            f'\n{DIAMOND} No̱ of Guilds In: `{len(self.bot.guilds)}`'\
            f'\n{DIAMOND} No̱ of Commands: `{len(self.bot.commands)}`'\
            f'\n{DIAMOND} Bot Storage Size: `{bstore} MB`'\
            f'\n{DIAMOND} Bot Memory: `{bmem} MB`'\
            f'\n{DIAMOND} Latency: `{round(self.bot.latency * 1000, 2)} ms`'\
            f'\n{DIAMOND} Owner: {f"<@{self.bot.owner_id}>" if self.bot.owner_id else "?"}'\
            f'\n{DIAMOND} Python Version: `{platform.python_version()}`'\
            f'\n{DIAMOND} Discord.py Version: `{dpy_version}`'

            embed.set_author(name=f'{self.bot.user.name}',icon_url=self.bot.user.avatar.url)
            embed.add_field(name='Bot', inline=False, value=bot_info)

            await ctx.send(embed=embed)

    @commands.command(aliases=['roleinfo'])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def role_info(self, ctx:commands.Context, *, role: discord.Role):
        """Shows information about a server role."""
        try:
            name = role.name

            members = []
            for index, member in enumerate(role.members):
                myName = member.nick or member
                members.append(str(myName))

            if len(members) == 0 or len(members) > 6:
                members = str(len(members))
            else:
                members = ', '.join(members)

            mentionable = role.mentionable
            position = role.position
            colour = role.colour
            created = role.created_at.strftime('%Y %b %d')

            permissions = []
            for index, permission in enumerate(role.permissions):
                if permission[1] == True:

                    permissions.append(
                        permission[0].upper().replace('_', ' '))
            if len(permissions) == 0:
                permissions = 'None'
            else:
                permissions = ', '.join(permissions)

        except:
            return await self.bot.send_error(ctx, f'{role} not found.')

        embed = discord.Embed(
            colour=colour,
            title=f'Information about this role:'
        )
        embed.set_author(
            name=f'{ctx.guild.name}',
            icon_url=ctx.guild.icon
        )
        embed.add_field(
            inline=True,
            name=f'**Name**: {name}',
            value=f'{DIAMOND}**Created**: {created}\n'
            + f'{DIAMOND}**Position**: {position}\n'
            + f'{DIAMOND}**Mentionable**: {mentionable}\n'
            + f'{DIAMOND}**Members**: {members}\n'
            + f'{DIAMOND}**Permissions**: {permissions}\n'
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['serverinfo'])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def server_info(self, ctx:commands.Context):
        """Shows information about this server."""
        server: discord.Guild = ctx.guild
        if not server: return await ctx.send(f'Server "{server}" not found.')

        no_of_bots = 0
        no_of_users = 0
        no_online = 0
        for member in ctx.guild.members:
            if member.bot:
                no_of_bots += 1
            else:
                no_of_users += 1
            if member.status.name == 'online':
                no_online += 1
        members = f'{no_of_users} users, {no_of_bots} bots, {no_online} online now'

        channels = f'{len(server.text_channels)} Text, '\
            f'{len(server.voice_channels)} Voice, {len(server.categories)} Categories'

        created_at = f'<t:{int(tea_time.mktime(server.created_at.timetuple()))}:D>, '\
            f'<t:{int(tea_time.mktime(server.created_at.timetuple()))}:R>'

        features = ', '.join([
            str(feature).replace('_',' ').capitalize()
            for feature in server.features
        ]) or 'None'

        embed = discord.Embed(
            title=f'Information About Server: {server.name}', colour = 0xa69f9c,
            description=f'{DIAMOND}**Members**: {members}\n'\
                f'{DIAMOND}**Channels**: {channels}\n'\
                f'{DIAMOND}**Owner**: <@{server.owner.id}>\n'\
                f'{DIAMOND}**Roles**: {len(server.roles)}\n'\
                f'{DIAMOND}**Created**: {created_at}\n'\
                f'{DIAMOND}**Features**: {features}\n'
        )

        if server.icon:
            embed.set_thumbnail(url=server.icon)
        if server.banner:
            embed.set_image(url=server.banner.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=['joined','userinfo'])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def user_info(self, ctx:commands.Context, *, member: Optional[discord.Member]):
        """Shows information about a member.
        Or shows information about yourself if none specified."""

        if ctx.current_argument == None:
            member = ctx.message.author
        elif member == None:
            return await self.bot.send_error(ctx, f'"{ctx.current_argument}" not found.')
        try:
            roles = []
            if member.top_role.name != '@everyone':
                roles.append(f'<@&{str(member.top_role.id)}>')
            for role in member.roles:
                if str(role.name) == '@everyone':
                    roles.append('@everyone')
                elif str(role.id) != str(member.top_role.id):
                    roles.append(f'<@&{str(role.id)}>')
            roles = '**Roles**: ' + ' '.join(roles) or ''

            status = str(member.status).capitalize() if not str(member.status) == 'dnd' else 'Do not disturb'
            is_bot = member.bot
            activity = member.activity

            try:
                if activity:
                    if activity.type == discord.ActivityType.listening:
                        if activity.name.casefold() == 'spotify':
                            activity = f'**Listening To**: [{activity.title}]({activity.track_url}), by {activity.artist}'
                        else:
                            activity = f'**Listening To**: {activity.name}'

                    elif activity.type == discord.ActivityType.playing:
                        activity = f'**Playing**: {activity.name}'

                    elif activity.type == discord.ActivityType.competing:
                        activity = f'**Competing In**: {activity.name}'

                    elif activity.type == discord.ActivityType.streaming:
                        activity = f'**Streaming**: [{activity.name}]({activity.url}) -- {activity.game}'

                    else:
                        activity = f'**Activity**: {activity.name}'

                    activity += '\n'
                else:
                    activity = ''
            except:
                activity = ''

            colour = member.colour
            created = f'<t:{int(tea_time.mktime(member.created_at.timetuple()))}:D>, '\
                f'<t:{int(tea_time.mktime(member.created_at.timetuple()))}:R>'
            joined = f'<t:{int(tea_time.mktime(member.joined_at.timetuple()))}:D>, '\
                f'<t:{int(tea_time.mktime(member.joined_at.timetuple()))}:R>'
            avatar = member.avatar
        except:
            return await self.bot.send_error(ctx, f'{member} not found.')

        embed = discord.Embed(
            colour=colour,
            title=f'Information About {"Bot" if is_bot else "User"}: **{member.display_name}**',
            description=f'{DIAMOND}**Global Display Name**: {member.global_name if member.global_name else member}\n'\
            f'{DIAMOND}**Status**: {status}\n'\
            f'{DIAMOND + activity if activity else ""}'\
            f'{DIAMOND}**Account Creation**: {created}\n'\
            f'{DIAMOND}**Joined Server**: {joined}\n'\
            f'{DIAMOND + roles if roles else ""}\n'
        )

        ua=await self.bot.fetch_user(member.id)
        if ua.banner:
            embed.set_image(url=ua.banner.url)
        embed.set_thumbnail(url=avatar)

        await ctx.send(embed=embed)

async def setup(bot: commands.bot):
    await bot.add_cog(Meta(bot))
