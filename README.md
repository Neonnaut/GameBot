# Discord-Gamesbot

This is an advanced Discord Bot that plays a few games and does a few other things.

## Setup

- In the [Discord developer portal](https://discord.com/developers/applications) create a new application and give it a name. Under `Bot` select "add bot"
- Under `Bot`, turn on PRESENCE INTENT, SERVER MEMBERS INTENT and MESSAGE CONTENT INTENT
- Generate an invite link for your bot under `QAuth2 > URL Generator`, with `bot` > `read messages/view channels`, `send messages`, `use external emojis` and `add reactions` permissions
- Use the invite link in your browser to invite your bot to your server
- under `Bot`, copy your bot's secret token. In your `.env.example` file, replace the "ccc" with your secret token. Save the file.
- Rename the file `.env.example` to `.env`. Make sure the file is called `.env` and _not_ ".env.txt"
- Install python 3.9+ Make sure you have set Python to the system path
- Install dependencies with `pip install REQUIREMENTS.txt`
- Run it as a module with `python gamesbot`, or `sudo nohup python3 gamesbot` or whatever command you use to run python scripts in your environment; or directly run the `__main__.py` file. Congratulations, you are now self-hosting a discord bot
- You might need to turn on all intents in the developer portal or change the bots intents in the `__main__.py` file
- If you do not want to self-host, I suggest using a VPS like Lenode, Heroku or [Fly.io](https://fly.io/docs/getting-started/)
