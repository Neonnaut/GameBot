import datetime as dt
import os
import random as r
import discord
from discord.ext import commands

"""
Outline:
Wargame ~Cog
  ~Start war
    warGame ~Command
    getPlayer
    getTypes
  ~Reset War
    warReset ~Command
  ~War Actions
    warMoves ~Command
    warMove
    anyTrue
    vicCond
    moveArm
    findArm
  ~Damage
    doDmg
    rollDice
    modDmg
    roundNum
  ~Board
    warShow ~Command
    printBoard
    num2str
  ~war Score
    warScore ~Command
~etc
  bool2yn
  copyBool
  copyStr
Setup
"""

MAX_WILL = 100
MAX_ARMY_COUNT = 9
RECORD_FILE = '.cogs/wargame/RECORDS.txt'
WARGAME_TIMEDELTA = dt.timedelta(minutes=1)

BLANK = '···'
ROCK = 'xxx'

class Wargame(commands.Cog, name='wargame'):
    """A turn based battle minigame played on a grid."""

    COG_EMOJI = '⚔️'

    def __init__(self, bot: commands.Bot):
        self.bot:discord.Client = bot

        self.run = False
        self.passes = 0
        self.moves = 0

        self.board = []  # ['--- AS1 AW2 --- ---', '--- XXX --- AS3 ---']...
        self.column_index = ''  # This will loop print the column index of the board
        self.col_start = 'F'  # i.e the first column of the board
        self.col_end = self.col_start  # Later will be K to Z depending on board size
        self.warCommand = ''

        self.blueUser = None  # User object
        self.blueUserDisplay = ''  # e.g: John [nationx]
        self.blueNationDisplay = ''  # e.g: [nationx]
        self.blueTurn = True
        self.blueTurns = []
        self.blueTypes = []
        self.blueAttack = []
        self.blueHealth = []
        self.blueMoral = []
        self.blueDemoral = []

        self.redUser = None
        self.redUserDisplay = ''
        self.redNationDisplay = ''
        self.redTurn = False
        self.redTurns = []
        self.redTypes = []
        self.redAttack = []
        self.redHealth = []
        self.redMoral = []
        self.redDemoral = []

    # [attacker_count] [attacker_RMIL] [attacker_RGOV] [attacker_WILL]
    # [defender_count] [defender_RMIL] [defender_RGOV] [defender_WILL]
    # Enter things in this order redCount, redRMIL, redRGOV, redWILL, blueCount, blueRMIL, blueRGOV, blueWILL
    @commands.command()
    @commands.guild_only()
    async def warGame(self, ctx:commands.Context,
                      attacker_count: int,
                      attacker_RMIL: int,
                      attacker_RGOV: int,
                      attacker_WILL: int,
                      defender_count: int,
                      defender_RMIL: int,
                      defender_RGOV: int,
                      defender_WILL: int
                      ):
        """Starts a new war between two players."""

        # Check if a game is not already running
        if self.run:
            return await self.bot.send_error(ctx, f'A game is already running.')
        else:
            # Setup the army stats
            self.run = True
            self.redTurn = False
            self.blueTurn = True
            for i in range(attacker_count):
                self.redTurns.append(await copyBool(self.redTurn))
                self.redAttack.append(attacker_RMIL)
                self.redHealth.append(max(1, attacker_RMIL) * 5)
                self.redDemoral.append(attacker_RGOV)
                self.redMoral.append(
                    max(1, int((attacker_WILL / MAX_WILL) * attacker_RGOV)) * 5)

            for i in range(defender_count):
                self.blueTurns.append(await copyBool(self.blueTurn))
                self.blueAttack.append(defender_RMIL)
                self.blueHealth.append(max(1, defender_RMIL) * 5)
                self.blueDemoral.append(defender_RGOV)
                self.blueMoral.append(
                    max(1, int((defender_WILL / MAX_WILL) * defender_RGOV)) * 5)

            # Get the red player.
            msg = await ctx.send('The attacker has 60 seconds to react to this message with :crossed_swords: ?')
            await msg.add_reaction('\N{CROSSED SWORDS}')
            await self.getPlayer(msg)
            if self.run == False:
                # We should get here if warReset has been used beforehand
                return
            elif self.redUser == None:
                await self.warReset(ctx)
                return await self.bot.send_error(ctx, 'Failed to get attacker.')

            # Get the blue player.
            msg = await ctx.send('The defender has 60 seconds to react to this message with :shield: ?')
            await msg.add_reaction('\N{SHIELD}')
            await self.getPlayer(msg)
            if self.run == False:
                # We should get here if warReset has been used beforehand
                return
            if self.blueUser == None:
                await self.warReset(ctx)
                return await self.bot.send_error(ctx, 'Failed to get defender.')

        # Setup the board
        if attacker_count > MAX_ARMY_COUNT or defender_count > MAX_ARMY_COUNT:
            await self.warReset(ctx)
            return await self.bot.send_error(ctx, 'The game has been hard-coded to refuse to play battles with over nine armies.')
        else:
            side_len = max(defender_count, attacker_count) + 2
            board = []

            for row in range(side_len):
                board.append([])
                for col in range(side_len):
                    board[row].append(await copyStr(BLANK))

            # Lay Defending Armies on The Board First
            lay_start = int(side_len / 2) - int(defender_count / 2)
            for i in range(defender_count):
                board[-1][lay_start + i] = 'D' + self.blueTypes[i] + str(i + 1)

            # Lay Attacking Armies on The Board Second
            lay_start = int(side_len / 2) - int(attacker_count / 2)
            for i in range(attacker_count):
                board[0][lay_start + i] = 'A' + \
                    self.redTypes[i] + str(i + 1)

            # Lay random rocks to break up the battlefield
            rock_count = max(attacker_count, defender_count)
            if rock_count >= 2:
                i = 0
                while i < rock_count:
                    row = r.randint(0, side_len - 1)
                    col = r.randint(0, side_len - 1)
                    if board[row][col] == BLANK:
                        board[row][col] = await copyStr(ROCK)
                        i += 1

            # Copy the board and get the last column
            self.board = self.copyBoard(board)
            self.col_end = chr(ord(self.col_start) + side_len)

            # Make the column header
            column_header = '\u200b \u200b \u200b'
            for col in range(len(self.board[0])):
                column_header += '  ' + \
                    chr(ord(self.col_start) + col).upper() + ' '
            column_header += ' \u200b\u200b\n'

            # Copy the board and the header
            self.column_index = await copyStr(column_header)

            await self.printBoard(ctx)

        self.warCommand = f'{ctx.clean_prefix}warGame {attacker_count} {attacker_RMIL} {attacker_RGOV} {attacker_WILL}'
        self.warCommand += f' {defender_count} {defender_RMIL} {defender_RGOV} {defender_WILL}'

    async def getPlayer(self, msg):
        # This function is only called by warGame for each player
        time_now = dt.datetime.now()
        answered = False

        while self.run and not answered and time_now + WARGAME_TIMEDELTA >= dt.datetime.now():
            msg = await msg.channel.fetch_message(msg.id)
            for reaction in msg.reactions:
                async for user in reaction.users():
                    # Make sure the reaction is not from the bot
                    if user.id == self.bot.user.id:
                        pass
                    elif reaction.emoji == '\N{CROSSED SWORDS}':
                        await msg.channel.send('Defender, please wait while the attacker chooses their army equipment.')

                        # Assign the attacking player as redUser
                        self.redUser = user

                        # Make user display name
                        userName = user.display_name
                        userNation = userName
                        if ('[' in userNation) and (']' in userNation):
                            userNation1 = userNation.find('[')
                            userNation2 = userNation.find(']')
                            userNation = userNation[userNation1 +
                                                    1:userNation2]
                            self.redNationDisplay = userNation
                        else:
                            userNation = ''
                            self.redNationDisplay = userName
                        self.redUserDisplay = userName

                        await self.getTypes(True, user)
                        answered = True
                    elif reaction.emoji == '\N{SHIELD}':
                        await msg.channel.send('Attacker, please wait while the defender chooses their army equipment.')

                        # Assign the defending player as blueUser
                        self.blueUser = user

                        # Make user display name
                        userName = user.display_name
                        userNation = userName
                        if ('[' in userNation) and (']' in userNation):
                            userNation1 = userNation.find('[')
                            userNation2 = userNation.find(']')
                            userNation = userNation[userNation1 +
                                                    1:userNation2]
                            self.blueNationDisplay = userNation
                        else:
                            self.blueNationDisplay = userName
                            userNation = ''
                        self.blueUserDisplay = userName

                        await self.getTypes(False, user)
                        answered = True

    async def getTypes(self, attacker, user):
        # This function is only called by getTypes for each player
        query = 'You have 60 seconds to decide. Will you equip\n'
        query += 'spears :chopsticks:\n'
        query += 'swords :crossed_swords:\n'
        query += 'or arrows :bow_and_arrow: ?\n\n'
        query += '**for army '

        armies = 0
        if attacker:
            armies = len(self.redAttack)
            self.redTypes = []
        else:
            armies = len(self.blueAttack)
            self.blueTypes = []

        for i in range(armies):
            # Send the query by DM to the player.
            query_msg = await user.send(query + str(i+1) + ':**')
            await query_msg.add_reaction('\N{CHOPSTICKS}')
            await query_msg.add_reaction('\N{CROSSED SWORDS}')
            await query_msg.add_reaction('\N{BOW AND ARROW}')

            # Ask for what types the armies will be in the DM.
            wait = True
            wait_time = dt.datetime.now()
            while wait and wait_time + WARGAME_TIMEDELTA > dt.datetime.now():
                query_msg = await query_msg.channel.fetch_message(query_msg.id)
                for r in query_msg.reactions:
                    async for u in r.users():
                        if u.id == self.bot.user.id:
                            pass
                        elif attacker and r.emoji == '\N{CHOPSTICKS}':
                            self.redTypes.append('S')
                            wait = False
                        elif attacker and r.emoji == '\N{CROSSED SWORDS}':
                            self.redTypes.append('W')
                            wait = False
                        elif attacker and r.emoji == '\N{BOW AND ARROW}':
                            self.redTypes.append('R')
                            wait = False
                        elif not attacker and r.emoji == '\N{CHOPSTICKS}':
                            self.blueTypes.append('S')
                            wait = False
                        elif not attacker and r.emoji == '\N{CROSSED SWORDS}':
                            self.blueTypes.append('W')
                            wait = False
                        elif not attacker and r.emoji == '\N{BOW AND ARROW}':
                            self.blueTypes.append('R')
                            wait = False

        # Make armies spear type if the player failed to select their types.
        if attacker and len(self.redTypes) < len(self.redAttack):
            for i in range(max(0, len(self.redAttack) - len(self.redTypes))):
                self.redTypes.append('S')

        elif not attacker and len(self.blueTypes) < len(self.blueAttack):
            for i in range(max(0, len(self.blueAttack) - len(self.blueTypes))):
                self.blueTypes.append('S')

    @commands.command()  # warReset
    @commands.guild_only()
    async def warReset(self, ctx:commands.Context):
        """Resets the war and ends any other wars."""

        self.run = False
        self.passes = 0
        self.moves = 0

        self.board = []
        self.column_index = ''
        self.col_end = self.col_start
        self.warCommand = ''

        self.blueUser = None
        self.blueUserDisplay = ''
        self.blueNationDisplay = ''
        self.blueTurn = True
        self.blueTurns = []
        self.blueTypes = []
        self.blueAttack = []
        self.blueHealth = []
        self.blueMoral = []
        self.blueDemoral = []

        self.redUser = None
        self.redUserDisplay = ''
        self.redNationDisplay = ''
        self.redTurn = False
        self.redTurns = []
        self.redTypes = []
        self.redAttack = []
        self.redHealth = []
        self.redMoral = []
        self.redDemoral = []

        await ctx.channel.send('The game has ended. The board has been reset.')

    @commands.command(name='wm')  # warMoves
    @commands.guild_only()
    async def warMoves(self, ctx:commands.Context, *args):
        """
        Possible moves:
        `|p|wm [army name 1] [target location 1] <army name 2> <target location 2>...`
        Moves your army to another location in the map. If the target destination has an enemy army, you attack it.

        `|p|wm wait`
        Passes your turn, but only three passes may happen in a row or the defender wins.

        `|p|wm [army name] escape`
        If your mentioned army is on the edge of the map, they may leave the game. You might do this to save them from death.
        """

        # Do pass move if the first argument is 'pass', otherwise send error message.
        if args[0].lower() == 'pass':
            await self.warMove(ctx, ['pass'])
        elif len(args) == 1:
            return await self.bot.send_error(ctx, 'One argument called "{args[0]}" not found.')

        # Else get the army and location pairs and do war move.
        else:
            cmd = []
            for i in range(len(args)):
                if args[i] == 'to' or args[i] == '2' or '|' in args[0]:
                    pass

                elif len(cmd) == 0:
                    cmd.append(args[i])

                elif len(cmd) == 1:
                    cmd.append(args[i])

                    # Do the warmove for the individual army e.g: ds2 a1
                    if self.run != False:
                        await self.warMove(ctx, cmd)
                    else:
                        return await self.bot.send_error(ctx, 'There is no game running at this time')
                        
                    # Reset the command
                    cmd = []

        # Send the board to the discord channel
        await self.printBoard(ctx)

    async def warMove(self, ctx:commands.Context, args):  # Non-command warMove
        if self.run == False:
            return await self.bot.send_error(ctx, 'There is no game running at this time')

        # Do pass move if argument is pass
        elif args[0].lower() == 'pass':
            for i in range(len(self.blueTurns)):
                self.blueTurns[i] = False

            for i in range(len(self.redTurns)):
                self.redTurns[i] = False

            self.passes += 1
            await ctx.send(str(self.passes) + ' / 3 passes have been used contiguously. If 3 are used contiguously, the defender automatically wins.')

        elif args[-1].lower() == 'run' or args[-1].lower() == 'rout' or args[-1].lower() == 'escape' and self.blueUser.id == ctx.author.id and 'd' in args[0].lower():
            (arm_row, arm_col) = await self.findArm(args[0])
            if arm_row == None or arm_col == None:
                await self.bot.send_error(ctx, 'That army was not found on the map')

            elif arm_row != 0 and arm_col != 0 and arm_row != len(self.board) - 1 and arm_col != len(self.board[0]) - 1:
                await self.bot.send_error(ctx, 'You must be at the edge of the map to run away')

            else:
                arm_ndx = int(args[0][2:]) - 1
                self.blueMoral[arm_ndx] = 0
                self.blueTurns[arm_ndx] = False
                self.board[arm_row][arm_col] = await copyStr(BLANK)
                self.moves += 1

        elif args[-1].lower() == 'run' or args[-1].lower() == 'rout' or args[-1].lower() == 'escape' and self.redUser.id == ctx.author.id and 'a' in args[0].lower():
            (arm_row, arm_col) = await self.findArm(args[0])
            if arm_row == None or arm_col == None:
                await self.bot.send_error(ctx, 'That army was not found on the map')

            elif arm_row != 0 and arm_col != 0 and arm_row != len(self.board) - 1 and arm_col != len(self.board[0]) - 1:
                await self.bot.send_error(ctx, 'You must be at the edge of the map to run away')

            else:
                arm_ndx = int(args[0][2:]) - 1
                self.redMoral[arm_ndx] = 0
                self.redTurns[arm_ndx] = False
                self.board[arm_row][arm_col] = await copyStr(BLANK)
                self.moves += 1

        elif not args[0][-1].isdigit():
            await self.bot.send_error(ctx, 'The selected unit input should be like DS1 or ds1. Please try again')

        elif not self.blueUser.id == ctx.author.id and not self.redUser.id == ctx.author.id:
            await self.bot.send_error(ctx, 'You don\'t have an offense or defense role')

        elif self.blueTurn and 'a' in args[0].lower() or self.redTurn and 'd' in args[0].lower():
            await self.bot.send_error(ctx, 'You may only move your own armies')

        elif not self.blueUser.id == ctx.author.id and self.redUser.id == ctx.author.id and not self.redTurn or self.blueUser.id == ctx.author.id and not self.redUser.id == ctx.author.id and not self.blueTurn:
            await self.bot.send_error(ctx, 'It is not your turn')

        elif self.blueTurn and not self.blueTurns[int(args[0][2:]) - 1] or self.redTurn and not self.redTurns[int(args[0][2:]) - 1]:
            await self.bot.send_error(ctx, 'You may only move each army once per turn')

        elif self.blueUser.id == ctx.author.id and self.blueTurn and 'd' in args[0].lower():
            if await self.moveArm(ctx, args):
                arm_ndx = int(args[0][2:]) - 1
                self.blueTurns[arm_ndx] = False
                self.moves += 1
                self.passes = 0

        elif self.redUser.id == ctx.author.id and self.redTurn and 'a' in args[0].lower():
            if await self.moveArm(ctx, args):
                arm_ndx = int(args[0][2:]) - 1
                self.redTurns[arm_ndx] = False
                self.moves += 1
                self.passes = 0
        else:
            await self.bot.send_error(ctx, 'There was some other problem')

        if not await self.anyTrue(self.blueTurns) and not await self.anyTrue(self.redTurns) or args[0].lower() == 'pass':
            self.blueTurn = not self.blueTurn
            self.redTurn = not self.redTurn

            for i in range(len(self.blueTurns)):
                self.blueTurns[i] = self.blueTurn and self.blueHealth[i] > 0 and self.blueMoral[i] > 0

            for i in range(len(self.redTurns)):
                self.redTurns[i] = self.redTurn and self.redHealth[i] > 0 and self.redMoral[i] > 0

            if self.blueTurn and self.moves >= len(self.blueTurns) or self.redTurn and self.moves >= len(self.redTurns):
                self.passes = 0
            self.moves = 0

        await self.vicCond(ctx)

    async def anyTrue(self, arr):  # Non-command
        any_true = False
        for i in arr:
            any_true = any_true or i
        return any_true

    # Check the conditions of a blue or red player victory.
    # This function is only called by warMove
    async def vicCond(self, ctx):
        blueVic = True
        redVic = True

        for i in range(len(self.redTurns)):
            blueVic = (self.redHealth[i] <=
                       0 or self.redMoral[i] <= 0) and blueVic

        if blueVic == False:
            for i in range(len(self.blueTurns)):
                redVic = (self.blueHealth[i] <=
                          0 or self.blueMoral[i] <= 0) and redVic
        else:
            redVic = False

        if self.passes >= 3:
            blueVic = True

        if blueVic:
            await ctx.send(f'🛡️ Congratulations, the defender, <@{self.blueUser.id}> has won this war against <@{self.redUser.id}>.' +
                           f'\nOriginal warGame command: `{self.warCommand}`')
            os.makedirs(os.path.dirname(RECORD_FILE), exist_ok=True)
            file_message = f'Defender: {self.blueUserDisplay}; won against: {self.redUserDisplay}. {dt.datetime.utcnow().strftime("%d.%b.%Y %H:%M")}\n'
            with open(RECORD_FILE, 'a') as f:
                f.write(file_message)
            await self.printBoard(ctx)
            await self.warReset(ctx)

        elif redVic:
            await ctx.send(f'⚔️ Congratulations, the attacker, <@{self.redUser.id}> has won this war against <@{self.blueUser.id}>.' +
                           f'\nOriginal warGame command: `{self.warCommand}`')
            os.makedirs(os.path.dirname(RECORD_FILE), exist_ok=True)
            file_message = f'Attacker: {self.redUserDisplay}; won against: {self.blueUserDisplay}; {dt.datetime.utcnow().strftime("%d.%b.%Y %H:%M")} UTC\n'
            with open(RECORD_FILE, 'a') as f:
                f.write(file_message)
            await self.printBoard(ctx)
            await self.warReset(ctx)

    # This function is only called by warMove
    async def moveArm(self, ctx:commands.context, args):
        target_row = None
        target_col = None

        (arm_row, arm_col) = await self.findArm(args[0])
        if arm_row == None or arm_col == None:
            await self.bot.send_error(ctx, 'That army was not found on the map')
            return False

        # Decode target position
        if len(args[-1]) >= 2 and args[-1][1:].isdigit() and ord(self.col_start.lower()) <= ord(args[-1][0].lower()) and ord(args[-1][0].lower()) < ord(self.col_end.lower()):
            target_row = int(args[-1][1:]) - 1
            target_col = ord(args[-1][0].lower()) - ord(self.col_start.lower())

        else:
            await self.bot.send_error(ctx, 'There is something wrong with the destination entered')
            return False

        # Check Distance
        if abs(arm_row - target_row) > 1 or abs(arm_col - target_col) > 1:
            mess = 'I\'m sorry, but the destination requested is too far away from the selected army.\n'
            mess += 'Army @ ' + str(arm_col) + ' ' + str(arm_row) + \
                ' | Target @ ' + str(target_col) + ' ' + str(target_row)
            await ctx.channel.send(mess)
            return False

        elif 'A' in self.board[arm_row][arm_col] and 'A' in self.board[target_row][target_col] or 'D' in self.board[arm_row][arm_col] and 'D' in self.board[target_row][target_col]:
            await self.bot.send_error(ctx, 'Attacking or moving on your own armies is not allowed')
            return False

        elif 'A' in self.board[arm_row][arm_col] and 'D' in self.board[target_row][target_col]:
            red_ndx = int(self.board[arm_row][arm_col][2]) - 1
            blue_ndx = int(self.board[target_row][target_col][2]) - 1

            await self.doDmg('red', blue_ndx, red_ndx)

            # Check if blue army is dead
            if self.blueHealth[blue_ndx] <= 0 or self.blueMoral[blue_ndx] <= 0:
                self.board[target_row][target_col] = await copyStr(BLANK)

            # Let blue army fight back if it's not dead
            else:
                await self.doDmg('blue', blue_ndx, red_ndx)

                if self.redHealth[red_ndx] <= 0 or self.redMoral[red_ndx] <= 0:
                    self.board[arm_row][arm_col] = await copyStr(BLANK)

            return True

        elif 'D' in self.board[arm_row][arm_col] and 'A' in self.board[target_row][target_col]:
            blue_ndx = int(self.board[arm_row][arm_col][2]) - 1
            red_ndx = int(self.board[target_row][target_col][2]) - 1

            await self.doDmg('blue', blue_ndx, red_ndx)

            # Check if red army is dead
            if self.redHealth[red_ndx] <= 0 or self.redMoral[red_ndx] <= 0:
                self.board[target_row][target_col] = await copyStr(BLANK)

            # Let red army fight back if it's not dead
            else:
                await self.doDmg('red', blue_ndx, red_ndx)

                if self.blueHealth[blue_ndx] <= 0 or self.blueMoral[blue_ndx] <= 0:
                    self.board[arm_row][arm_col] = await copyStr(BLANK)

            return True

        elif self.board[target_row][target_col] == ROCK:
            await self.bot.send_error(ctx, 'There is a boulder in the way. You may not move there')
            return False

        elif self.board[target_row][target_col] == BLANK:
            self.board[target_row][target_col] = self.board[arm_row][arm_col]
            self.board[arm_row][arm_col] = await copyStr(BLANK)
            return True

        else:
            await self.bot.send_error(ctx, 'There was some other problem')
            return False

    # loop through the board and find the army matching the inputted army and
    # return the position of the army on the board. If army is not found, return None
    async def findArm(self, arm):
        arm_row = None
        arm_col = None

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if arm.lower() == self.board[row][col].lower():
                    arm_row = row
                    arm_col = col
                    break
            if arm_row != None and arm_col == None:
                break

        if arm_row == None or arm_col == None:
            return (None, None)
        else:
            return (arm_row, arm_col)

    # Do damage on warMove to an army
    # blue_or_red refers to which team is doing the damage
    # blue_ndx and red_ndx refer to the id of the arms, i.e: the number in 'AS1'
    async def doDmg(self, blue_or_red, blue_ndx, red_ndx):
        if blue_or_red == 'blue':
            dmg = await self.rollDice(max(1, int(self.blueAttack[blue_ndx] / 2)), 3)
            dmg = await self.modDmg(dmg, self.blueTypes[blue_ndx], self.redTypes[red_ndx])
            self.redHealth[red_ndx] = max(0, self.redHealth[red_ndx] - dmg)

            demoral = await self.rollDice(max(1, int(self.blueDemoral[blue_ndx] / 2)), 3)
            demoral = await self.modDmg(demoral, self.blueTypes[blue_ndx], self.redTypes[red_ndx])
            self.redMoral[red_ndx] = max(
                0, self.redMoral[red_ndx] - demoral)

        elif blue_or_red == 'red':
            dmg = await self.rollDice(max(1, int(self.redAttack[red_ndx] / 2)), 3)
            dmg = await self.modDmg(dmg, self.redTypes[red_ndx], self.blueTypes[blue_ndx])
            self.blueHealth[blue_ndx] = max(
                0, self.blueHealth[blue_ndx] - dmg)

            demoral = await self.rollDice(max(1, int(self.redDemoral[red_ndx] / 2)), 3)
            demoral = await self.modDmg(demoral, self.redTypes[red_ndx], self.blueTypes[blue_ndx])
            self.blueMoral[blue_ndx] = max(
                0, self.blueMoral[blue_ndx] - demoral)

        return None

    async def rollDice(self, count, faces):
        sum = 0
        for i in range(count):
            sum += r.randint(1, faces)
        return sum

    async def modDmg(self, dmg, attacker_type, defender_type):
        modifier = 1.3333333333

        if attacker_type == 'S' and defender_type == 'W':
            dmg = await self.roundNum(dmg * modifier)
        elif attacker_type == 'W' and defender_type == 'R':
            dmg = await self.roundNum(dmg * modifier)
        elif attacker_type == 'R' and defender_type == 'S':
            dmg = await self.roundNum(dmg * modifier)

        return dmg

    async def roundNum(self, num):
        if num - int(num) >= 0.5:
            return int(num) + 1
        else:
            return int(num)

    @commands.command()  # warShow
    @commands.guild_only()
    async def warShow(self, ctx:commands.Context):
        """Shows the current game being played."""
        if (self.run == False):
            return await self.bot.send_error(ctx, 'There is no game running')
        elif (self.blueUser == None and self.redUser == None):
            return await self.bot.send_error(ctx, 'A game is running, but there were no players found')
        else:
            try:
                await ctx.channel.send(f'{self.redNationDisplay} vs. {self.blueNationDisplay}:')
                await self.printBoard(ctx)
            except:
                return await self.bot.send_error(ctx, 'Something went wrong')

    async def printBoard(self, ctx):
        red_len = len(self.redHealth)
        blue_len = len(self.blueHealth)

        # Make the board and the index

        if self.run == False:
            return
        else:
            # Build the INDEX array
            index = []
            for row in range(len(self.board)):
                index.append([])
                for col in range(len(self.board[0])):
                    index[row].append(
                        chr(ord(self.col_start) + col) + str(row + 1))

            # print(self.board[0])
            # Count Screen Width
            screen_width = len(self.board[0]) * len(BLANK)
            screen_width += len(self.board[0])
            screen_width += 3
            #screen_width += len(self.board[0]) * 4

            # Write the header to the snapshot

            snap = ''
            snap += self.column_index #///

            # Merge the board and index in the same snapshot
            # Write the row index
            row_index = 1
            for row in range(len(self.board)):
                snap += ''

                snap += str(row_index)
                if row_index < 10:
                    snap += '  '
                else:
                    snap += ' '
                row_index += 1

                # Write the board
                for col in range(len(self.board[0])):
                    if self.board[row][col].startswith('A'):
                        snap = snap + '[2;31m' + self.board[row][col] + '[0m' + ' '
                    elif self.board[row][col].startswith('D'):
                        snap = snap + '[2;34m' + self.board[row][col] + '[0m' + ' '
                    else:
                        snap = snap + self.board[row][col] + ' '

                snap += '\n'

            snap = f'```ansi\n{snap}```'

            # Print Table Header
            # Print the units header
            snap2 = '     '
            for i in range(red_len):
                snap2 += 'A' + self.redTypes[i] + str(i + 1) + ' '
            snap2 += '| '

            for i in range(blue_len):
                snap2 += 'D' + self.blueTypes[i] + str(i + 1) + ' '

            # Print hitpoints
            snap2 += '\n'
            snap2 += 'HitP '

            for i in range(red_len):
                snap2 = snap2 + await num2str(3, self.redHealth[i]) + ' '

            snap2 += '| '
            for i in range(blue_len):
                snap2 = snap2 + await num2str(3, self.blueHealth[i]) + ' '

            # Print moral
            snap2 += '\n'
            snap2 += 'Morl '

            for i in range(red_len):
                snap2 = snap2 + await num2str(3, self.redMoral[i]) + ' '

            snap2 += '| '
            for i in range(blue_len):
                snap2 = snap2 + await num2str(3, self.blueMoral[i]) + ' '

            # Print turn
            snap2 += '\n'
            snap2 += 'Turn '

            for i in range(red_len):
                y_or_n = await bool2yn(self.redTurns[i])
                snap2 = snap2 + await num2str(3, y_or_n) + ' '

            snap2 += '| '
            for i in range(blue_len):
                y_or_n = await bool2yn(self.blueTurns[i])
                snap2 = snap2 + await num2str(3, y_or_n) + ' '

            # Print types
            snap2 += '\n'
            snap2 += 'Type '

            # Print the type to the table
            for i in range(red_len):
                myType = self.redTypes[i]
                if myType == 'S':
                    myType = 'Spr'
                elif myType == 'W':
                    myType = 'sWd'
                elif myType == 'R':
                    myType = 'aRr'
                snap2 = snap2 + await num2str(3, myType) + ' '
            snap2 += '| '
            for i in range(blue_len):
                myType = self.blueTypes[i]
                if myType == 'S':
                    myType = 'Spr'
                elif myType == 'W':
                    myType = 'sWd'
                elif myType == 'R':
                    myType = 'aRr'
                snap2 = snap2 + await num2str(3, myType) + ' '

            snap2 = f'```{snap2}```'

            if self.redTurns[0]:
                currentusr = (self.redUser.display_name[:15].strip() + '...') if len(self.redUser.display_name) > 18 else self.redUser.display_name
            else:
                currentusr = (self.blueUser.display_name[:15].strip() + '...') if len(self.blueUser.display_name) > 18 else self.blueUser.display_name

            do_inline=False
            if screen_width <= 20:
                do_inline=True

            await ctx.channel.send(f'**{currentusr}\'s turn now**{snap}{snap2}')

    def copyBoard(self, board):
        copied_board = []

        for row in range(len(board)):
            copied_board.append([])
            for col in range(len(board[row])):
                copied_board[row].append(board[row][col])

        return copied_board

    @ commands.command(name='warScore')  # warScore
    @ commands.has_permissions(administrator=True)
    async def warScore(self, ctx:commands.Context):
        """For administors only. This shows recorded victories."""
        try:
            await ctx.send(file=discord.File(RECORD_FILE))
        except:
            return await self.bot.send_error(ctx, 'Could not reach the file. Perhaps it doesn\'t exist yet')

async def num2str(cnt, num):
    num = str(num)

    cnt = cnt - len(num)

    if cnt < 0:
        cnt = 0

    for i in range(cnt):
        num = ' ' + num

    return num

async def bool2yn(bool):
    if bool:
        return 'Y'
    else:
        return 'N'

async def copyBool(bool):
    if bool:
        return True
    else:
        return False

async def copyStr(s):
    return (str(s) + '.')[:-1]

# Adds the cog on bot start up
async def setup(bot: commands.bot):
    await bot.add_cog(Wargame(bot))