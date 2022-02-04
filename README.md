# discord_bot_collection

A collection of discord bots created with Python using the enhanced-dpy module

## Installation instructions (linux)

1. install python3.10

2. run `python3.10 -m venv .venv`

3. run `source .venv/bin/activate`

4. run `pip install git+https://github.com/iDevision/enhanced-discord.py`

5. run `pip install -r requirements.txt`

6. create a file named `.env` and add your API Token to it like this:

```env
API_TOKEN="<your API Token>"
```

## Running the bot

- For testing purposes just running it with `python bot.py` inside your venv is fine.

- `bot.sh` contains an exemplary script to run the bot once the venv is set up. Just edit the path to wherever you cloned the repository to and run it with `./bot.sh <start/stop>`
