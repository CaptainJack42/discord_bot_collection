import asyncio

import discord
import misc.variables as var
from discord.ext import commands
from misc.bot_logger import get_logger


class PurgeBot(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = get_logger()

    @commands.command(
        name="delete",
        aliases=["purge", "del", "rm"],
        pass_context=True,
        help="deletes <amount> messages from the channel",
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, limit: int = None):
        if limit is not None:
            await ctx.channel.purge(limit=limit + 1)
            info = await ctx.send(embed=discord.Embed(description=f"Deleted {limit} messages", color=var.C_GREEN))
            self.logger.info(f"{ctx.author} deleted {limit} messages in {ctx.channel.name} of {ctx.guild.name}")
            await asyncio.sleep(2)
            await info.delete()

        else:
            await ctx.send(
                embed=discord.Embed(
                    description=(
                        "🚫 You need to define the amount to delete messages too! Make sure the amount is numerical."
                    ),
                    color=var.C_RED,
                ).add_field(name="Format", value=f"`{var.PREFIX}purge <amount>`")
            )

    @commands.command(name="spam", pass_context=True, help="Spams <amount> messages in the channel")
    @commands.has_permissions(manage_messages=True)
    async def spam(self, ctx: commands.Context, arg: str):
        for i in range(int(arg + 1)):
            await ctx.send(f"--- {i} --- spam")
        await ctx.send("okay enough spam")


def setup(bot: commands.Bot):
    bot.add_cog(PurgeBot(bot))
