from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_CLIENT = os.getenv('DISCORD_CLIENT')
PREFIX = '!!'
ACTIVITY = f'Waiting for {PREFIX} commands'
DESCRIPTION = 'A bot that plays a battle minigame.'
TESTING = True if os.getenv('TESTING') == 'True' else False
STARTTIME = datetime.utcnow()

# Emojis
CHECK = '✅>'
ERR = '❌'
WARN = '⚠️'
DIAMOND = '🔸'