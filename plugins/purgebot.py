import discord
from discord.ext import commands
from misc.bot_logger import get_logger


class PurgeBot(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = get_logger()

    @commands.command(name="delete", aliases=["purge", "del", "rm"], pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, arg: str):
        try:
            msgs = list()
            num = int(arg) + 1
            async for msg in ctx.channel.history(limit=num):
                msgs.append(msg)
            await ctx.channel.delete_messages(msgs)
        except discord.errors.HTTPException:
            await ctx.send("can only delete messages that are under 14 Days old")
        except Exception as e:
            await ctx.send(f"encountered {str(e)}")
            self.logger.error(f"{ctx.message.content} (purge command) encountered {str(e)}")


def setup(bot: commands.Bot):
    bot.add_cog(PurgeBot(bot))
