from discord.ext import commands


class PurgeBot(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def purge(self, ctx):
        await ctx.send("purging...")


def setup(bot: commands.Bot):
    bot.add_cog(PurgeBot(bot))
