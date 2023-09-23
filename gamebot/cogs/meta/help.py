import operator
from typing import Optional, Set
import discord
from discord import Embed
from discord.ext import commands
from constants import ERR, PREFIX

def assign_prefix(prefix, message):
    return message.replace('|p|', PREFIX).replace('|h|', prefix)

class HelpDropdown(discord.ui.Select):
    def __init__(self, help_command: 'MyHelpCommand', options: list[discord.SelectOption]):
        super().__init__(placeholder='Choose a category...',
                         min_values=1, max_values=1, options=options)
        self._help_command = help_command

    async def callback(self, interaction: discord.Interaction):
        embed = (
            await self._help_command.cog_help_embed(self._help_command.context.bot.get_cog(self.values[0]))
        )
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, help_command: 'MyHelpCommand', options: list[discord.SelectOption], *, timeout: Optional[float] = 120.0):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(help_command, options))
        self._help_command = help_command

    async def on_timeout(self):
        # remove dropdown from message on timeout
        self.clear_items()
        await self._help_command.response.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self._help_command.context.author == interaction.user


class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command: commands.Command):
        return f'{command.qualified_name} {command.signature}'

    def __init__(self):
        attrs = {
        #    'hidden': True,
            'help': f'The command used to show this message.\nUse `{PREFIX}help [command]` for help on a command or group of commands.'
        }   
        super().__init__(command_attrs=attrs)

    async def _cog_select_options(self) -> list[discord.SelectOption]:
        unsorted_options = {}
        options: list[discord.SelectOption] = []

        for cog, command_set in self.get_bot_mapping().items():
            filtered = await self.filter_commands(command_set, sort=True)
            if not filtered:
                continue
            emoji = getattr(cog, 'COG_EMOJI', None)
            cog_name = cog.qualified_name if cog else 'No-Category'
            option = discord.SelectOption(
                label=cog_name.capitalize(),
                value=cog_name,
                emoji=emoji,
                description=cog.description[:100] if cog and cog.description else None
            ) 
            unsorted_options.update(
                {cog_name: option})
            
        for c_name, c_option in sorted(unsorted_options.items()): # Alphabetise this
            options.append(
                c_option
            )

        return options

    async def _help_embed(
        self, title: str, description: Optional[str] = None, mapping: Optional[str] = None,
        command_set: Optional[Set[commands.Command]] = None, set_author: bool = False,
        set_footer: bool = False
    ) -> Embed:
        embed = Embed(title=title, colour = 0xa69f9c)
        if description:
            embed.description = description
        if set_author:
            avatar = self.context.bot.user.avatar or self.context.bot.user.default_avatar
            embed.set_author(name=self.context.bot.user.name,
                             icon_url=avatar.url)
        if command_set:
            # show help about all commands in the set
            filtered = await self.filter_commands(command_set, sort=True)
            for command in filtered:
                my_help = assign_prefix(self.context.clean_prefix,command.help or '...') if command.help else '...'
                embed.add_field(
                    name=f'{self.get_command_signature(command).strip().capitalize()}',
                    value=my_help[:250].strip() + '...' if len(my_help) > 253 else my_help,
                    inline=False
                )
        elif mapping:
            # add a short description of commands in each cog
            unsorted_cogs = {}

            e = mapping.items()

            for cog, command_set in mapping.items():
                filtered = await self.filter_commands(command_set, sort=True)
                if not filtered:
                    continue
                name = cog.qualified_name.capitalize() if cog else 'No category'
                emoji = getattr(cog, 'COG_EMOJI', None)
                cog_label = f'{emoji} {name}' if emoji else name
                # \u2002 is an en-space
                cmd_list = '\u2002 '.join(
                    f'{cmd.name.capitalize()}' for cmd in filtered
                )
                command_list = (
                    f'{cmd_list}'
                    if cog and cog.description
                    else cmd_list
                )
                unsorted_cogs.update({cog.qualified_name: [cog_label, command_list]})
            for c_name, c_option in sorted(unsorted_cogs.items()): # Alphabetise this
                embed.add_field(name=c_option[0], value=c_option[1], inline=False)
        if set_footer:
            embed.set_footer(text=set_footer)
        return embed

    async def bot_help_embed(self, mapping: dict) -> Embed:
        return await self._help_embed(
            title='Bot Commands',
            description=f'Type `{self.context.clean_prefix}help <command>` for more info on a command. \
                You can choose a category for more info by using the dropdown list, or type `{self.context.clean_prefix}help <category>`',
            mapping=mapping,
            set_author=True,
        )

    async def send_bot_help(self, mapping: dict):
        embed = await self.bot_help_embed(mapping)
        options = await self._cog_select_options()
        self.response = await self.get_destination().send(embed=embed, view=HelpView(self, options))

    # Help on a specific command
    async def send_command_help(self, command: commands.Command):
        emoji = getattr(command.cog, 'COG_EMOJI', None)
        if isinstance(command, commands.Group):
            embed = await self._help_embed(
                title=f'{emoji} {self.get_command_signature(command).strip().capitalize()}' if emoji else self.get_command_signature(command),
                description=f'\n\n{assign_prefix(self.context.clean_prefix,command.help or "...")}\nUse `help{self.context.clean_prefix}<command>` for help on an individual command.',
                command_set=command.commands,
                set_footer=None
            )
        else:
            embed = await self._help_embed(
                title=f'{emoji} {self.get_command_signature(command).strip().capitalize()}' if emoji else self.get_command_signature(command),
                description=f'\n\n{assign_prefix(self.context.clean_prefix,command.help or "...")}',
                command_set=None,
                set_footer='Command aliases: '+', '.join(map(str,command.aliases)) if command.aliases else None
            )
        await self.get_destination().send(embed=embed)

    async def cog_help_embed(self, cog: Optional[commands.Cog]) -> Embed:
        if cog is None:
            return await self._help_embed(
                title=f'No category',
                command_set=self.get_bot_mapping()[None]
            )
        emoji = getattr(cog, 'COG_EMOJI', None)
        myCommands = cog.get_commands()
        if len(myCommands) == 1:
            command = myCommands[0]
            if isinstance(command, commands.Group):
                return await self._help_embed(
                    title=f'{emoji} {self.get_command_signature(command).strip().capitalize()}' if emoji else self.get_command_signature(command),
                    description=f'\n\n{assign_prefix(self.context.clean_prefix,command.help or "...")}\nUse `help{self.context.clean_prefix}<command>` for help on an individual command.',
                    command_set=command.commands if isinstance(
                        command, commands.Group) else None,
                        set_footer='Command aliases: '+', '.join(map(str,command.aliases)) if command.aliases else None
                )
        return await self._help_embed(
            title=f'{emoji} {cog.qualified_name.capitalize()}' if emoji else cog.qualified_name.capitalize(),
            description=f'{cog.description}\nUse `help{self.context.clean_prefix}<command>` for help on an individual command.',
            command_set=cog.get_commands()
        )

    # Send help about a category (AKA: cog)
    async def send_cog_help(self, cog: commands.Cog):
        embed = await self.cog_help_embed(cog)
        await self.get_destination().send(embed=embed)

    # Use the same function as command help for group help
    send_group_help = send_command_help

    async def command_not_found(self, message):
        return f'{ERR} Command "{message}" not found.'
