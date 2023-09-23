from random import SystemRandom
from typing import Optional

import discord
import sympy
from constants import CHECK
from discord.ext import commands


class Games(commands.Cog, name='games'):
    """Games like Chess, Wordle or a flag guessing game."""
    COG_EMOJI = '🕹️'

    def __init__(self, bot: discord.Client):
        self.bot:discord.Client = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def choose(self, ctx:commands.Context, first:str, second:str, third:Optional[str]):
        """Chooses a random option from two to three options.
        Example: `|p|choose "Helena Rubinstein" Cher "Margot Robbie"`"""
        choice = SystemRandom().choice([first, second, third])
        await ctx.reply(choice, mention_author=False)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coinflip(self, ctx:commands.Context, coin: Optional[str]):
        """Flips a coin and returns heads or tails."""
        result = SystemRandom().choice(['heads', 'tails'])
        if coin:
            mess=f'{"You chose "+coin.casefold()} {"but"if coin.casefold()!=result else"and"} the'
        else:
            mess='The'
        await ctx.reply(f'{mess} result was {result}', mention_author=False) 

    @commands.hybrid_command(aliases=['r','dice','rol','rll'],
        description='Rolls dice in the format <№_dice>d<№_sides>, in the range <1-10>d<2-100>.')
    @discord.app_commands.describe(dice='A number of sides, or NdN, in the range <1-10>d<2-100>',
        modifier='A number to add or subtract from the total')
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def roll(self, ctx:commands.Context, dice:str, *, modifier:Optional[str]):
        """
        Rolls dice in the format <№_of_dice>d<№_of_sides>, in the range <1-10>d<2-100>.
        You can optionally add a + or - modifier to the result.
        Example: `|h|roll 2d100 -3`

        You can also specify a single dice with just it's number of faces.
        Example: `|h|roll 3`
        """
        amount = 0
        die = 0
        rolls = []
        total = 0
        myModifier = modifier
        if not modifier:
            modifier = ''

        errorMessage = []
        goodMessage = []

        if 'd' in dice:
            amount, die = dice.split('d')
            if die.isdigit() and amount.isdigit():
                die = int(die)
                amount = int(amount)
                if 1 <= amount <= 100:
                    if 2 <= die <= 100:
                        for _ in range(amount):
                            roll = SystemRandom().randrange(1, die+1)
                            rolls.append(roll)
                        if len(rolls) == 1:
                            goodMessage.append(f'Result: **{rolls[0]}**')
                        else:
                            strRolls = ''
                            for roll in rolls:
                                strRolls += f'**{roll}**, '
                            strRolls = strRolls[:-2]
                            strRolls = f'{strRolls}'
                            goodMessage.append(f'Result: {strRolls}')
                    else:
                        errorMessage.append('The die must be in the range 2 to 100')
                else:
                    errorMessage.append('The amount of dice must be in the range 1 to 100')
            else:
                errorMessage.append('The requested dice roll was not in the format NdN')
        elif dice.isdigit():
            die = int(dice)
            dice = f'1d{dice}'
            if 2 <= die <= 100:
                roll = SystemRandom().randrange(1, die+1)
                rolls.append(roll)
                goodMessage.append(f'Result:** {roll}**')
            else:
                errorMessage.append('The amount of dice must be in the range 1 to 10')
        else:
            errorMessage.append('The requested dice roll was not in the format NdN')

        # Modifier
        if myModifier != None:
            if len(myModifier) < 6:
                try:
                    myModifier = myModifier.replace('**', '')
                    myModifier = myModifier.replace('*', '')
                    myModifier = myModifier.replace('/', '')
                    myModifier = sympy.sympify(myModifier)
                    myModifier = f'{myModifier}'

                    myModifier = int(myModifier)
                    if myModifier < 0:
                        modifier = f'- {str(myModifier).replace("-", "")}'
                    else:
                        modifier = f'+ {myModifier}'
                    goodMessage.append(f'Modifier: **{modifier}**')
                except:
                    myModifier = 0
                    errorMessage.append('Modifiers should look like `+ 300` or `- 20`')
            else:
                myModifier = 0
                errorMessage.append('Modifiers cannot exceed 5 digits')
        else:
            myModifier = 0

        # Total
        for roll in rolls:
            total += roll
        total += myModifier
        if myModifier == 0 and len(rolls) == 1:
            pass
        else:
            goodMessage.append(f'Total: **{total}**')

        # Colour
        if len(errorMessage) == 0:
            first = str(total)[0]
            last = str(total)[-1]
            if first == '-':
                colour = 0x000000 # black
            elif last == '1':
                colour = 0x523110 # brown
            elif last == '2':
                colour = 0xBA0202 # red
            elif last == '3':
                colour = 0xFE7000 # orange
            elif last == '4':
                colour = 0xDBA800 # yellow
            elif last == '5':
                colour = 0x07B307 # green
            elif last == '6':
                colour = 0x0067C4 # blue
            elif last == '7':
                colour = 0x7F40BF # purple
            elif last == '8':
                colour = 0x696969 # grey
            elif last == '9':
                colour = 0xf2efed # white
            else:
                colour = 0x000000 # black

            # Send
            embed = discord.Embed(
                title=f'Roll {dice} {modifier}',
                description=f', '.join(goodMessage),
                colour=colour
            )
            await ctx.reply(embed=embed, mention_author=False)
        else:
            return await self.bot.send_error(ctx, '. '.join(errorMessage))

async def setup(bot: commands.bot):
    await bot.add_cog(Games(bot))