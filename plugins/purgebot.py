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
        if arg == "all" or arg == "*":
            await ctx.channel.clone()
            await ctx.channel.delete()
            return
        try:
            msgs = list()
            num = int(arg) + 1
            async for msg in ctx.channel.history(limit=num):
                msgs.append(msg)
            await ctx.channel.delete_messages(msgs)
        except discord.errors.HTTPException:
            await ctx.send("can only delete messages that are under 14 Days old")
        except ValueError:
            await ctx.send("Argument needs to be a number between 1 and 99 or `all`")
        except Exception as e:
            await ctx.send(f"encountered {str(e)}")
            self.logger.error(f"{ctx.message.content} (purge command) encountered {str(e)}")

    @commands.command(name="spam", pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def spam(self, ctx: commands.Context, arg: str):
        for _ in range(int(arg)):
            await ctx.send("spam")
        await ctx.send("okay enough spam")


def setup(bot: commands.Bot):
    bot.add_cog(PurgeBot(bot))
