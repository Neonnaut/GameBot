'''
http://xahlee.info/comp/unicode_index.html

This site helps me for discord reactions.
'''


import discord
from discord.ext import tasks, commands

import datetime as dt
import asyncio

import random as r

'''
TODO?
make it so that inputting the army name doesn't require the unit type
fix board to be able to have more than 7 armies
Have army location data stored in WarGame instead of purely the map
'''

delay = 0.05
war_game = False

intents = discord.Intents.default()
intents.members = True

bot_name = 'GameBot'
blank = '---'
rock = 'XXX'
spacer = 5
time_delta = dt.timedelta(minutes=1)

class file:
	error_report_file_name = ''
	error_report_message = ''

def copyBoard( board ):
	copied_board = []
	
	for row in range( len( board ) ):
		copied_board.append( [] )
		for col in range( len( board[ row ] ) ):
			copied_board[ row ].append( board[ row ][ col ] )
	
	return copied_board

class WarGame:
	run = False
	blueTurn = True
	redTurn = False
	blueUser = None
	redUser = None
	
	redTurns = []
	redAttack = []
	redHealth = []
	redMoral = []
	redDemoral = []
	redTypes = []
	
	blueTurns = []
	blueAttack = []
	blueHealth = []
	blueMoral = []
	blueDemoral = []
	blueTypes = []
	
	header = ''
	board = []
	col_start = 'F'
	col_end = col_start
	dt = None
	passes = 0
	moves = 0

#Make the bot object
token = ''
with open('token.txt') as token_file:
	token = token_file.readline()

bot = commands.Bot(command_prefix='++', intents=intents)

@bot.command()
async def speak(ctx, *args):
	await asyncio.sleep(delay)
	await ctx.send('woof!')
	
	'''
	f = open( error_report_file_name, 'w' )
	f.write( error_report_message )
	f.close()
	'''
	
	'''
	msg = await ctx.send('Will you be an attacker :crossed_swords:\nor a defender :shield:')
	await msg.add_reaction( '\N{CROSSED SWORDS}' )
	await msg.add_reaction( '\N{SHIELD}' )
	await getTypes(msg)
	'''
	
	'''
	await msg.add_reaction( '\N{CHOPSTICKS}' )
	await msg.add_reaction( '\N{CROSSED SWORDS}' )
	await msg.add_reaction( '\N{BOW AND ARROW}' )
	
	WarGame.dt = dt.datetime.now()
	'''

'''
@bot.event
async def on_reaction_add(reaction, user):
	if WarGame.dt == None:
		print('None')
	elif WarGame.dt + dt.timedelta(minutes=1) < dt.datetime.now():
		print('Too Late')
	elif reaction.emoji == '\N{CHOPSTICKS}':
		print('Chopsticks')
		await user.send('Chopsticks')
	elif reaction.emoji == '\N{CROSSED SWORDS}':
		print('Swords')
		await user.send('Swords')
	elif reaction.emoji == '\N{BOW AND ARROW}':
		print('Bow')
		await user.send('Bow')
	else:
		print('oops')
		await user.send('oops')
	
	print( reaction )
	print( str( reaction ) )
	
	if WarGame.dt != None and WarGame.dt + dt.timedelta(minutes=1) >= dt.datetime.now() and reaction == '\N{CHOPSTICKS}':
		print('chopsticks')
	
	WarGame.dt = None
'''

@bot.command()
async def warReset(ctx):
	WarGame.run = False
	WarGame.redTurn = False
	WarGame.blueTurn = True
	
	if WarGame.blueUser != None:
		role = discord.utils.get( ctx.guild.roles, name='Blue Team' )
		await WarGame.blueUser.remove_roles(role)
	WarGame.blueUser = None
	
	if WarGame.redUser != None:
		role = discord.utils.get( ctx.guild.roles, name='Red Team' )
		await WarGame.redUser.remove_roles(role)
	WarGame.redUser = None
	
	WarGame.redTurns = []
	WarGame.redAttack = []
	WarGame.redHealth = []
	WarGame.redMoral = []
	WarGame.redDemoral = []
	WarGame.redTypes = []
	
	WarGame.blueTurns = []
	WarGame.blueAttack = []
	WarGame.blueHealth = []
	WarGame.blueMoral = []
	WarGame.blueDemoral = []
	WarGame.blueTypes = []
	
	WarGame.header = ''
	WarGame.board = []
	WarGame.col_end = WarGame.col_start
	WarGame.passes = 0
	WarGame.moves = 0
	error_report_file_name = ''
	error_report_message = ''
	
	await ctx.channel.send( 'The game has ended. The board has been reset.' )

@bot.command()
async def helpme(ctx):
	help_message = ''
	with open('help.txt') as help_file:
		help_message = help_file.read()

	await ctx.channel.send( help_message )

async def rollDice( count, faces ):
	sum = 0
	for i in range( count ):
		sum += r.randint( 1, faces )
	return sum

async def num2str( cnt, num ):
	num = str( num )
	
	cnt = cnt - len( num )
	
	if cnt < 0:
		cnt = 0
	
	for i in range( cnt ):
		num = ' ' + num
	
	return num

async def bool2yn( bool ):
	if bool:
		return 'Y'
	else:
		return 'N'

async def printBoard(ctx):
	red_len = len( WarGame.redHealth )
	blue_len = len( WarGame.blueHealth )

	#Make the board and the index
	
	index = []
	for row in range( len( WarGame.board ) ):
		index.append([])
		for col in range( len( WarGame.board[0] ) ):
			index[row].append( chr( ord( WarGame.col_start ) + col ) + str( row + 1 ) )
	
	print( len( WarGame.board[0] ), WarGame.board[0] )
	#Count Screen Width
	screen_width = len( WarGame.board[0] ) * len( blank )
	screen_width += len( WarGame.board[0] )
	screen_width += spacer
	screen_width += len( WarGame.board[0] ) * 4
	
	#Write the header to the snapshot
	
	snap = ''
	snap += WarGame.header
	
	#Merge the board and index in the same snapshot
	for row in range( len( WarGame.board ) ):
		snap += '`'
		
		#Write the board
		for col in range( len( WarGame.board[0] ) ):
			snap = snap + WarGame.board[row][col] + ' '
		
		#Add spacer between the board and the index
		for col in range ( spacer ):
			snap += ' '
		
		#Write the index
		for col in range( len( index[0] ) ):
			snap = snap + index[row][col] + '  '
		
		snap += '`\n'
	
	#Print a line space
	snap += '`'
	for i in range( screen_width ):
		snap += ' '
	snap += '`\n'
	
	#Print Table Header
	snap += '`     '
	for i in range( red_len ):
		snap += 'A' + WarGame.redTypes[i] + str( i + 1 ) + ' '
	snap += '| '
	
	for i in range( blue_len ):
		snap += 'D' + WarGame.blueTypes[i] + str( i + 1 ) + ' '
	
	snap += '`\n'
	snap += '`HitP '
	
	for i in range( red_len ):
		snap = snap + await num2str( 3, WarGame.redHealth[ i ] ) + ' '
	
	snap += '| '
	for i in range( blue_len ):
		snap = snap + await num2str( 3, WarGame.blueHealth[ i ] ) + ' '
	
	snap += '`\n'
	snap += '`Morl '
	
	for i in range( red_len ):
		snap = snap + await num2str( 3, WarGame.redMoral[ i ] ) + ' '
	
	snap += '| '
	for i in range( blue_len ):
		snap = snap + await num2str( 3, WarGame.blueMoral[ i ] ) + ' '
	
	snap += '`\n'
	snap += '`Turn '
	
	for i in range( red_len ):
		y_or_n = await bool2yn( WarGame.redTurns[i] )
		snap = snap + await num2str( 3, y_or_n ) + ' '
	
	snap += '| '
	for i in range( blue_len ):
		y_or_n = await bool2yn( WarGame.blueTurns[i] )
		snap = snap + await num2str( 3, y_or_n ) + ' '
	
	snap += '`'
	
	await ctx.channel.send( snap )

async def copyBool( bool ):
	if bool:
		return True
	else:
		return False

async def copyStr( s ):
	return ( str( s ) + '.')[:-1]

async def getTypes( attacker, user ):
	query = 'You have 60 seconds to decide. Will you equip\n'
	query += 'spears :chopsticks:\n'
	query += 'swords :crossed_swords:\n'
	query += 'or bows :bow_and_arrow:\n\n'
	query += '**for army '
	
	armies = 0
	if attacker:
		armies = len( WarGame.redAttack )
		WarGame.redTypes = []
	else:
		armies = len( WarGame.blueAttack )
		WarGame.blueTypes = []
	
	for i in range( armies ):
		query_msg = await user.send( query + str(i+1) + '.**' )
		await query_msg.add_reaction( '\N{CHOPSTICKS}' )
		await query_msg.add_reaction( '\N{CROSSED SWORDS}' )
		await query_msg.add_reaction( '\N{BOW AND ARROW}' )
		
		wait = True
		wait_time = dt.datetime.now()
		while wait and wait_time + time_delta > dt.datetime.now():
			query_msg = await query_msg.channel.fetch_message( query_msg.id )
			for r in query_msg.reactions:
				async for u in r.users():
					if u.name == bot_name:
						pass
					elif attacker and r.emoji == '\N{CHOPSTICKS}':
						WarGame.redTypes.append( 'S' )
						wait = False
					elif attacker and r.emoji == '\N{CROSSED SWORDS}':
						WarGame.redTypes.append( 'W' )
						wait = False
					elif attacker and r.emoji == '\N{BOW AND ARROW}':
						WarGame.redTypes.append( 'R' )
						wait = False
					elif not attacker and r.emoji == '\N{CHOPSTICKS}':
						WarGame.blueTypes.append( 'S' )
						wait = False
					elif not attacker and r.emoji == '\N{CROSSED SWORDS}':
						WarGame.blueTypes.append( 'W' )
						wait = False
					elif not attacker and r.emoji == '\N{BOW AND ARROW}':
						WarGame.blueTypes.append( 'R' )
						wait = False
	
	if attacker and len( WarGame.redTypes ) < len( WarGame.redAttack ):
		for i in range( max( 0, len( WarGame.redAttack ) - len( WarGame.redTypes ) ) ):
			WarGame.redTypes.append( 'S' )
		
	elif not attacker and len( WarGame.blueTypes ) < len( WarGame.blueAttack ):
		for i in range( max( 0, len( WarGame.blueAttack ) - len( WarGame.blueTypes ) ) ):
			WarGame.blueTypes.append( 'S' )

async def getPlayer(msg):
	time_now = dt.datetime.now()
	answered = False
	
	while not answered and time_now + time_delta >= dt.datetime.now():
		msg = await msg.channel.fetch_message( msg.id )
		for reaction in msg.reactions:
			async for user in reaction.users():
				if user.name == bot_name:
					pass
				elif reaction.emoji == '\N{CROSSED SWORDS}':
					await msg.channel.send('Defender, please wait while the attacker chooses their army equipment.')
					
					role = discord.utils.get( msg.guild.roles, name='Red Team' )
					await user.add_roles(role)
					WarGame.redUser = user
					
					await getTypes( True, user )
					answered = True
				elif reaction.emoji == '\N{SHIELD}':
					await msg.channel.send('Attacker, please wait while the defender chooses their army equipment.')
					
					role = discord.utils.get( msg.guild.roles, name='Blue Team' )
					await user.add_roles(role)
					WarGame.blueUser = user
					
					await getTypes( False, user )
					answered = True

#Enter things in this order redCount, redRITR, redRGOV, redWILL, blueCount, blueRITR, blueRGOV, blueWILL
@bot.command()
async def warGame(ctx, *args):
	cmd_count = 8
	max_will = 100
	are_digits = True
	
	redCount = 0
	redRITR = 1
	redRGOV = 2
	redWILL = 3
	blueCount = 4
	blueRITR = 5
	blueRGOV = 6
	blueWILL = 7
	
	error_report_file_name = dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%p')
	
	# Setup the army stats
	for i in range( len( args ) ):
		are_digits = are_digits and args[i].isdigit()
	
	if WarGame.run:
		await ctx.channel.send( 'I am sorry. However, a Game is already running.' )
	
	elif len( args ) != cmd_count:
		await ctx.channel.send( 'I am sorry. However, there should be ' + str( cmd_count ) + ' arguments in your command.' )
	
	elif not are_digits:
		await ctx.channel.send( 'I am sorry. However, all arguments should be digits.' )
	
	else:
		WarGame.run = True
		WarGame.redTurn = False
		WarGame.blueTurn = True
		
		for i in range( int( args[ redCount ] ) ):
			WarGame.redTurns.append( await copyBool( WarGame.redTurn ) )
			WarGame.redAttack.append( int( args[ redRITR ] ) )
			WarGame.redHealth.append( max( 1, int( args[ redRITR ] ) ) * 5 )
			WarGame.redDemoral.append( int( args[ redRGOV ] ) )
			WarGame.redMoral.append( max( 1, int( ( int( args[ redWILL ] ) / max_will ) * int( args[ redRGOV ] ) ) ) * 5 )
		
		for i in range( int( args[ blueCount ] ) ):
			WarGame.blueTurns.append( await copyBool( WarGame.blueTurn ) )
			WarGame.blueAttack.append( int( args[ blueRITR ] ) )
			WarGame.blueHealth.append( max( 1, int( args[ blueRITR ] ) ) * 5 )
			WarGame.blueDemoral.append( int( args[ blueRGOV ] ) )
			WarGame.blueMoral.append( max( 1, int( ( int( args[ blueWILL ] ) / max_will ) * int( args[ blueRGOV ] ) ) ) * 5 )
		
		msg = await ctx.send('The attacker has 60 seconds to react to this message with :crossed_swords: ?')
		await msg.add_reaction( '\N{CROSSED SWORDS}' )
		await getPlayer(msg)
		msg = await ctx.send('The defender has 60 seconds to react to this message with :shield: ?')
		await msg.add_reaction( '\N{SHIELD}' )
		await getPlayer(msg)
	
	#Setup the board
	
	if args[blueCount].isdigit() and args[redCount].isdigit():
		side_len = max( int( args[blueCount] ), int( args[redCount] ) ) + 2
		board = []
		
		for row in range( side_len ):
			board.append( [] )
			for col in range( side_len ):
				board[row].append( await copyStr( blank ) )
		
		#Lay Defending Armies on The Board First
		lay_start = int( side_len / 2 ) - int( int( args[blueCount] ) / 2 )
		for i in range( int( args[blueCount] ) ):
			board[-1][ lay_start + i ] = 'D' + WarGame.blueTypes[i] + str( i + 1 )
		
		#Lay Attacking Armies on The Board Second
		lay_start = int( side_len / 2 ) - int( int( args[redCount] ) / 2 )
		for i in range( int( args[redCount] ) ):
			board[0][ lay_start + i ] = 'A' + WarGame.redTypes[i] + str( i + 1 )
		
		#Lay random rocks to break up the battlefield
		rock_count = max( int( args[redCount] ), int( args[blueCount] ) )
		if rock_count >= 2:
			i = 0
			while i < rock_count:
				row = r.randint( 0, side_len - 1 )
				col = r.randint( 0, side_len - 1 )
				if board[row][col] == blank:
					board[row][col] = await copyStr( rock )
					i += 1
		
		#Make the Header
		header = 'BOARD'
		header2 = 'INDEX'
		screen_board_len = ( ( len( blank ) + 1 ) * side_len ) - len( header ) + spacer
		header = '`' + header
		for i in range( screen_board_len ):
			header += ' '
		
		header += header2
		screen_index_len = ( ( len( blank ) + 1 ) * side_len ) - len( header2 )
		for i in range( screen_index_len ):
			header += ' '
		
		header += '`\n'
		
		#Copy the board and the header
		WarGame.header = await copyStr( header )
		WarGame.board = copyBoard( board )
		WarGame.col_end = chr( ord( WarGame.col_start ) + side_len )
		
		await printBoard(ctx)
	
	else:
		await ctx.channel.send( 'I am sorry. However, the army counts must be digits.' )
		await warReset(ctx)
		return None

async def roundNum( num ):
	if num - int(num) >= 0.5:
		return int(num) + 1
	else:
		return int(num)

async def modDmg( dmg, attacker_type, defender_type ):
	modifier = 1.3333333333
	
	if attacker_type == 'S' and defender_type == 'W':
		dmg = await roundNum( dmg * modifier )
	elif attacker_type == 'W' and defender_type == 'R':
		dmg = await roundNum( dmg * modifier )
	elif attacker_type == 'R' and defender_type == 'S':
		dmg = await roundNum( dmg * modifier )
	
	return dmg

async def doDmg( blue_or_red, blue_ndx, red_ndx ):
	if blue_or_red == 'blue':
		dmg = await rollDice( max( 1, int( WarGame.blueAttack[blue_ndx] / 2 ) ), 3 )
		dmg = await modDmg( dmg, WarGame.blueTypes[blue_ndx], WarGame.redTypes[red_ndx] )
		WarGame.redHealth[red_ndx] = max( 0, WarGame.redHealth[red_ndx] - dmg )
		
		demoral = await rollDice( max( 1, int( WarGame.blueDemoral[blue_ndx] / 2 ) ), 3 )
		demoral = await modDmg( demoral, WarGame.blueTypes[blue_ndx], WarGame.redTypes[red_ndx] )
		WarGame.redMoral[red_ndx] = max( 0, WarGame.redMoral[red_ndx] - demoral )
	
	elif blue_or_red == 'red':
		dmg = await rollDice( max( 1, int( WarGame.redAttack[red_ndx] / 2 ) ), 3 )
		dmg = await modDmg( dmg, WarGame.redTypes[red_ndx], WarGame.blueTypes[blue_ndx] )
		WarGame.blueHealth[blue_ndx] = max( 0, WarGame.blueHealth[blue_ndx] - dmg )
		
		demoral = await rollDice( max( 1, int( WarGame.redDemoral[red_ndx] / 2 ) ), 3 )
		demoral = await modDmg( demoral, WarGame.redTypes[red_ndx], WarGame.blueTypes[blue_ndx] )
		WarGame.blueMoral[blue_ndx] = max( 0, WarGame.blueMoral[blue_ndx] - demoral )
	
	return None

async def findArm(arm):
	arm_row = None
	arm_col = None
	
	for row in range( len( WarGame.board ) ):
		for col in range( len( WarGame.board[row] ) ):
			if arm.lower() == WarGame.board[row][col].lower():
				arm_row = row
				arm_col = col
				break
		if arm_row != None and arm_col == None:
			break
	
	if arm_row == None or arm_col == None:
		return (None, None)
	else:
		return (arm_row, arm_col)
		

async def moveArm(ctx, args):
	target_row = None
	target_col = None
	
	(arm_row, arm_col) = await findArm( args[0] )
	if arm_row == None or arm_col == None:
		await ctx.channel.send( 'I am sorry. However, that army was not found on the map.' )
		return False
	
	#Decode target position
	if len( args[-1] ) >= 2 and args[-1][1:].isdigit() and ord( WarGame.col_start.lower() ) <= ord(args[-1][0].lower()) and ord( args[-1][0].lower() ) < ord( WarGame.col_end.lower() ):
		target_row = int( args[-1][1:] ) - 1
		target_col = ord( args[-1][0].lower() ) - ord( WarGame.col_start.lower() )
	
	else:
		await ctx.channel.send( 'I am sorry. However, there is something wrong with the destination entered.' )
		return False
	
	#Check Distance
	if abs(arm_row - target_row) > 1 or abs(arm_col - target_col) > 1:
		mess = 'I am sorry. However, the destination requested is too far away from the selected army.\n'
		mess += 'Army @ ' + str(arm_col) + ' ' + str(arm_row) + ' | Target @ ' + str(target_col) + ' ' + str(target_row)
		await ctx.channel.send( mess )
		return False
	
	elif 'A' in WarGame.board[ arm_row ][ arm_col ] and 'A' in WarGame.board[ target_row ][ target_col ] or 'D' in WarGame.board[ arm_row ][ arm_col ] and 'D' in WarGame.board[ target_row ][ target_col ]:
		await ctx.channel.send( 'I am sorry. However, attacking or moving on your own armies is not allowed.' )
		return False
	
	elif 'A' in WarGame.board[ arm_row ][ arm_col ] and 'D' in WarGame.board[ target_row ][ target_col ]:
		red_ndx = int( WarGame.board[ arm_row ][ arm_col ][ 2 ] ) - 1
		blue_ndx = int( WarGame.board[ target_row ][ target_col ][ 2 ] ) - 1
		
		await doDmg( 'red', blue_ndx, red_ndx )
		
		if WarGame.blueHealth[blue_ndx] <= 0 or WarGame.blueMoral[blue_ndx] <= 0:
			WarGame.board[ target_row ][ target_col ] = await copyStr( blank )
		
		else:
			await doDmg( 'blue', blue_ndx, red_ndx )
			
			if WarGame.redHealth[red_ndx] <= 0 or WarGame.redMoral[red_ndx] <= 0:
				WarGame.board[ arm_row ][ arm_col ] = await copyStr( blank )
		
		return True
	
	elif 'D' in WarGame.board[ arm_row ][ arm_col ] and 'A' in WarGame.board[ target_row ][ target_col ]:
		blue_ndx = int( WarGame.board[ arm_row ][ arm_col ][ 2 ] ) - 1
		red_ndx = int( WarGame.board[ target_row ][ target_col ][ 2 ] ) - 1
		
		await doDmg( 'blue', blue_ndx, red_ndx )
		
		if WarGame.redHealth[red_ndx] <= 0 or WarGame.redMoral[red_ndx] <= 0:
			WarGame.board[ target_row ][ target_col ] = await copyStr( blank )
		
		else:
			await doDmg( 'red', blue_ndx, red_ndx )
			
			if WarGame.blueHealth[ blue_ndx ] <= 0 or WarGame.blueMoral[ blue_ndx ] <= 0:
				WarGame.board[ arm_row ][ arm_col ] = await copyStr( blank )
		
		return True
	
	elif WarGame.board[target_row][target_col] == rock:
		ctx.send('I am sorry. However, there is a boulder in the way. You may not move there.')
		return False
	
	elif WarGame.board[ target_row ][ target_col ] == blank:
		WarGame.board[target_row][target_col] = WarGame.board[arm_row][arm_col]
		WarGame.board[arm_row][arm_col] = await copyStr( blank )
		return True
	
	else:
		await ctx.channel.send( 'I am sorry. However, there was some other problem.' )
		return False

async def vicCond(ctx):
	blueVic = True
	redVic = True
	
	file.error_report_message += 'Blue Turns: '
	for i in range( len( WarGame.blueTurns ) ):
		file.error_report_message = file.error_report_message + str( WarGame.blueTurns[i] ) + ' '
	
	file.error_report_message += '\nRed Turns: '
	for i in range( len( WarGame.redTurns ) ):
		file.error_report_message = file.error_report_message + str( WarGame.redTurns[i] ) + ' '
	
	file.error_report_message += '\nRed Vic Loop:\n'
	for i in range( len( WarGame.blueTurns ) ):
		redVic = ( WarGame.blueHealth[i] <= 0 or WarGame.blueMoral[i] <= 0 ) and redVic
		file.error_report_message = file.error_report_message + 'i: ' + str( i ) + ' '
		file.error_report_message = file.error_report_message + 'blueHealth: ' + str( WarGame.blueHealth ) + ' '
		file.error_report_message = file.error_report_message + 'blueMoral: ' + str( WarGame.blueMoral ) + ' '
		file.error_report_message = file.error_report_message + 'redVic: ' + str( redVic ) + ' '
		
	file.error_report_message += '\nBlue Vic Loop:\n'
	for i in range( len( WarGame.redTurns ) ):
		blueVic = ( WarGame.redHealth[i] <= 0 or WarGame.redMoral[i] <= 0 ) and blueVic
		file.error_report_message = file.error_report_message + 'i: ' + str( i ) + ' '
		file.error_report_message = file.error_report_message + 'redHealth: ' + str( WarGame.redHealth ) + ' '
		file.error_report_message = file.error_report_message + 'redMoral: ' + str( WarGame.redMoral ) + ' '
		file.error_report_message = file.error_report_message + 'blueVic: ' + str( blueVic ) + ' '
	
	file.error_report_message = file.error_report_message + '\nPasses Check: ' + str( WarGame.passes ) + ' '
	if WarGame.passes >= 3:
		blueVic = True
	
	file.error_report_message = file.error_report_message + 'Passes: ' + str( WarGame.passes ) + ' '
	file.error_report_message = file.error_report_message + 'blueVic: ' + str( blueVic ) + ' '
	file.error_report_message = file.error_report_message + 'redVic: ' + str( redVic ) + '\n\n\n\n'
	
	if blueVic:
		await ctx.send('Congratuations, the defender, ' + WarGame.blueUser.name + ', has won this war.')
		await printBoard(ctx)
		await warReset(ctx)
		
		error_report_file_name = dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%p')
		with open( 'Error_Report_' + error_report_file_name + '.txt', 'w') as f:
			f.write( file.error_report_message )
		
	elif redVic:
		await ctx.send('Congratuations, the attacker, ' + WarGame.redUser.name + ', has won this war.')
		await printBoard(ctx)
		await warReset(ctx)
		
		error_report_file_name = dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%p')
		with open( 'Error_Report_' + error_report_file_name + '.txt', 'w') as f:
			f.write( file.error_report_message )
		
async def allTrue( arr ):
	all_true = True
	for i in arr:
		all_true = all_true and i
	return all_true

async def anyTrue( arr ):
	any_true = False
	for i in arr:
		any_true = any_true or i
	return any_true

async def warMove( ctx, args ):
	roles = ctx.author.roles
	role_names = [ roles[i].name for i in range( len( roles ) ) ]
	
	if WarGame.run == False:
		await ctx.channel.send( 'I am sorry. However, there is no game running at this time' )
	
	elif args[0].lower() == 'pass' or args[0].lower() == 'wait':
		for i in range( len( WarGame.blueTurns ) ):
			WarGame.blueTurns[i] = False
		
		for i in range( len( WarGame.redTurns ) ):
			WarGame.redTurns[i] = False
		
		WarGame.passes += 1
		await ctx.send( str(WarGame.passes) + ' / 3 passes have been used contiguously. If 3 are used contiguously, the defender automatically wins.')
		
	elif args[-1].lower() == 'run' or args[-1].lower() == 'rout' or args[-1].lower() == 'escape' and 'Blue Team' in role_names and 'd' in args[0].lower():
		(arm_row, arm_col) = await findArm( args[0] )
		if arm_row == None or arm_col == None:
			await ctx.send('I am sorry. However, that army was not found on the map.')
			
		elif arm_row != 0 and arm_col != 0 and arm_row != len( WarGame.board ) - 1 and arm_col != len( WarGame.board[0] ) - 1:
			await ctx.send('I am sorry. However, you must be at the edge of the map to run away.')
		
		else:
			arm_ndx = int( args[0][2:] ) - 1
			WarGame.blueMoral[arm_ndx] = 0
			WarGame.blueTurns[arm_ndx] = False
			WarGame.board[arm_row][arm_col] = await copyStr( blank )
			WarGame.moves += 1
	
	elif args[-1].lower() == 'run' or args[-1].lower() == 'rout' or args[-1].lower() == 'escape' and 'Red Team' in role_names and 'a' in args[0].lower():
		(arm_row, arm_col) = await findArm( args[0] )
		if arm_row == None or arm_col == None:
			await ctx.send('I am sorry. However, that army was not found on the map.')
			
		elif arm_row != 0 and arm_col != 0 and arm_row != len( WarGame.board ) - 1 and arm_col != len( WarGame.board[0] ) - 1:
			await ctx.send('I am sorry. However, you must be at the edge of the map to run away.')
		
		else:
			arm_ndx = int( args[0][2:] ) - 1
			WarGame.redMoral[arm_ndx] = 0
			WarGame.redTurns[arm_ndx] = False
			WarGame.board[arm_row][arm_col] = await copyStr( blank )
			WarGame.moves += 1
	
	elif not args[0][-1].isdigit():
		await ctx.channel.send( 'I am sorry. However, the selected unit input should be like DS1 or ds1. Please try again.' )
	
	elif not 'Blue Team' in role_names and not 'Red Team' in role_names:
		await ctx.channel.send('I am sorry. However, you don\'t have an offense or defense role')
	
	elif WarGame.blueTurn and 'a' in args[0].lower() or WarGame.redTurn and 'd' in args[0].lower():
		await ctx.channel.send('I am sorry. However, you may only move your own armies.')
	
	elif not 'Blue Team' in role_names and 'Red Team' in role_names and not WarGame.redTurn or 'Blue Team' in role_names and not 'Red Team' in role_names and not WarGame.blueTurn:
		await ctx.channel.send( 'I am sorry. However, it is not your turn.' )
	
	elif WarGame.blueTurn and not WarGame.blueTurns[ int( args[0][2:] ) - 1 ] or WarGame.redTurn and not WarGame.redTurns[ int( args[0][2:] ) - 1 ]:
		await ctx.channel.send( 'I am sorry. However, you may only move each army once per turn.' )
	
	elif 'Blue Team' in role_names and WarGame.blueTurn and 'd' in args[0].lower():
		if await moveArm(ctx, args):
			arm_ndx = int( args[0][2:] ) - 1
			WarGame.blueTurns[arm_ndx] = False
			WarGame.moves += 1
	
	elif 'Red Team' in role_names and WarGame.redTurn and 'a' in args[0].lower():
		if await moveArm(ctx, args):
			arm_ndx = int( args[0][2:] ) - 1
			WarGame.redTurns[arm_ndx] = False
			WarGame.moves += 1
	
	else:
		await ctx.channel.send( 'I am sorry. However, there was some other problem.' )
	
	if not await anyTrue( WarGame.blueTurns ) and not await anyTrue( WarGame.redTurns ) or args[0].lower() == 'pass':
		WarGame.blueTurn = not WarGame.blueTurn
		WarGame.redTurn = not WarGame.redTurn
		
		for i in range( len( WarGame.blueTurns ) ):
			WarGame.blueTurns[i] = WarGame.blueTurn and WarGame.blueHealth[i] > 0 and WarGame.blueMoral[i] > 0
		
		for i in range( len( WarGame.redTurns ) ):
			WarGame.redTurns[i] = WarGame.redTurn and WarGame.redHealth[i] > 0 and WarGame.redMoral[i] > 0
		
		if WarGame.blueTurn and WarGame.moves >= len( WarGame.blueTurns ) or WarGame.redTurn and WarGame.moves >= len( WarGame.redTurns ):
			WarGame.passes = 0
		WarGame.moves = 0
		
	await vicCond(ctx)

@bot.command( aliases = ['wm'] )
async def warMoves( ctx, *args ):
	
	if args[0].lower() == 'pass':
		await warMove( ctx, ['pass'] )
	
	else:
		cmd = []
		for i in range( len( args ) ):
			if args[i] == 'to' or args[i] == '2' or '|' in args[0]:
				pass
			
			elif len( cmd ) == 0:
				cmd.append( args[i] )
			
			elif len( cmd ) == 1:
				cmd.append( args[i] )
				await warMove( ctx, cmd )
				cmd = []
	
	await printBoard( ctx )

@bot.command()
async def warShow(ctx):
	await printBoard(ctx)

@bot.command()
async def sleep(ctx):
	if ctx.author == ctx.guild.owner:
		await asyncio.sleep(delay)
		await ctx.send('I will sleep now.')
		await asyncio.sleep(delay)
		await bot.close()
	else:
		await ctx.channel.send( 'I am afraid I cannot do that. Only the server owner may put me to sleep.' )

bot.run(token)