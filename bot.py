import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from misc.bot_logger import get_logger

bot = commands.Bot(command_prefix="!", help_command=commands.DefaultHelpCommand(), intents=discord.Intents().all())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    LOGGER.info(f"{bot.user.display_name} connected in [{*bot.guilds,}]")


@bot.command(
    name="source", aliases=["code", "git"], description="Get the link to the github repository", pass_context=True
)
async def get_source(ctx: commands.Context):
    await ctx.send(
        f"The source code for this bot can be found here: https://github.com/CaptainJack42/discord_bot_collection \n\n\
        Feel free to report Bugs there or create a pull request if you already fixed them."
    )


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
    global LOGGER
    LOGGER = get_logger()
    for filename in os.listdir("./plugins"):
        if filename.endswith(".py"):
            bot.load_extension(f"plugins.{filename[:-3]}")
    bot.run(API_TOKEN)
