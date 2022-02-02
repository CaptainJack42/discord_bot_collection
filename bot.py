#!  /usr/bin/env python3.9

import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="!", help_command=commands.DefaultHelpCommand())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    LOGGER.info(f"{bot.user.display_name} connected in [{*bot.guilds,}]")


def setup_logger():
    log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format, filename=("debug.log"))
    file_handler = logging.FileHandler("SoR-Log.log")
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.DEBUG)
    global LOGGER
    LOGGER = logging.getLogger("SoR-Logger")
    LOGGER.addHandler(file_handler)


class MyHelpCommand(commands.HelpCommand):
    """[summary]
    currenctly unused.
    Can be used in the future to implement an own version of the help command.
    Args:
        commands ([type]): [description]
    """

    async def send_bot_help(self, mapping):
        await self.context.send("send_help")


if __name__ == "__main__":
    load_dotenv()
    API_TOKEN = os.environ.get("TEST_API_TOKEN")
    setup_logger()
    for filename in os.listdir("./plugins"):
        if filename.endswith(".py"):
            bot.load_extension(f"plugins.{filename[:-3]}")
    bot.run(API_TOKEN)
