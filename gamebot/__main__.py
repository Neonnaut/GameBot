import logging, os#, aiohttp
from logging.handlers import RotatingFileHandler
from difflib import SequenceMatcher

from discord import Intents, CustomActivity
from discord.ext import commands

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from constants import ACTIVITY, DESCRIPTION, DISCORD_CLIENT, PREFIX, TESTING, ERR, WARN

def main():
    logging_config()
    global logger
    logger=logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    bot = MyBot( # define an instance of the bot class to be run
        command_prefix=commands.when_mentioned_or(PREFIX),
        activity=CustomActivity(name=ACTIVITY),
        description=DESCRIPTION,
        intents=Intents().all(), case_insensitive=True,
    )
    bot.run(DISCORD_CLIENT, log_handler=None) # Run this bot instance

class MyBot(commands.Bot):
    async def setup_hook(self):
        # For HTTP requests
        #self.session = aiohttp.ClientSession()
        # Set the bot owner id. This is used for is_owner checks.
        application_info = await self.application_info()
        self.owner_id = application_info.owner.id
        # Load cogs from the cogs folder
        for cog in sorted(os.listdir('./cogs')):
            if cog.endswith('.py'):
                cog = cog[:-3]
            if not cog.startswith('_'):
                try:
                    await self.load_extension('cogs.' + cog)
                except Exception as e:
                    logger.error(str(e))
        # Log that the bot is starting
        logger.info(f'Logged in as {self.user.name} '\
            f'in {"testing" if TESTING else "working"} environment.')

    async def on_command_error(self, ctx:commands.Context, e): # Error messages
        try:
            if isinstance(e,(commands.CommandInvokeError, commands.HybridCommandError)):
                logger.exception(e)
                return await self.send_error(ctx, f'{e}')
            elif isinstance(e, commands.CommandNotFound):
                suggestion = ctx.message.content.replace(ctx.prefix, '').split(' ')
                available_commands = [cmd.name for cmd in self.commands]
                matches = {cmd:SequenceMatcher(None, cmd, suggestion[0]).ratio()
                    for cmd in available_commands}
                suggestion[0] = max(matches.items(), key=lambda item: item[1])[0]
                e=f'{e}. Did you mean `{ctx.prefix}{" ".join(suggestion)}`?'
            elif isinstance(e, commands.MissingRequiredArgument):
                e=f'{e} Run `{ctx.prefix}help {ctx.command}` for help on this command'
            return await self.send_error(ctx, f'{e}', emoji=WARN)
        except:
            await ctx.author.send(f'{ERR} I was unable to send feedback about command '\
                +f'"{ctx.message.content.replace(ctx.prefix, "").split(" ")[0][:20]}"'\
                +f' in "{ctx.message.channel.name}". '\
                +f'With error message: {e}{""if str(e)[-1]in[".","!","?"]else"."}')
            
    async def send_error(self, ctx:commands.Context, message:str, emoji=ERR):
        """Sends error message and deletes both messages."""
        message = str(message)
        await ctx.reply(f'{emoji} {message[:1].upper()}'\
            f'{message[1:]}{""if str(message)[-1]in[".","!","?"]else"."}',
            mention_author=False,delete_after=8)
        try:
            await ctx.message.delete(delay=8)
        except Exception:
            pass

class LoggerFormatter(logging.Formatter):
    """Logging Formatter to add colours and count warning / errors"""
    LEVEL_COLOURS = [(logging.CRITICAL, '\x1b[41;1m'), (logging.WARNING, '\x1b[33;1m'),
                     (logging.ERROR, '\x1b[31;1m'), (logging.INFO, '\x1b[32;1m'),
                     (logging.DEBUG, '\x1b[36;1m'), (logging.NOTSET, '\x1b[37;1m')]

    FORMATS={level:logging.Formatter(f'%(asctime)s.%(msecs)03d {colour}%(levelname)-8s'\
            f'\033[0m%(message)s \033[35m%(module)s:%(filename)s:%(lineno)d '\
            f'(%(funcName)s)\033[0m', '%Y-%b-%d %H:%M:%S')
        for level, colour in LEVEL_COLOURS}

    def format(self,record): return self.FORMATS.get(record.levelno).format(record)

def logging_config():
    root_logger=logging.getLogger()
    root_logger.setLevel(logging.WARNING)

    file_handler=RotatingFileHandler(filename='bot.log',maxBytes=1048576,backupCount=2)
    file_handler.setLevel(logging.WARNING) # Only file logs of level warning or above
    file_handler.setFormatter(LoggerFormatter())
    root_logger.addHandler(file_handler)

    console_handler=logging.StreamHandler() # Display console log levels via a loggers level
    console_handler.setFormatter(LoggerFormatter())
    root_logger.addHandler(console_handler)

if __name__ == '__main__':
    main()