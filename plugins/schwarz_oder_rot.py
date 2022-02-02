import discord
import misc.variables as var
from discord.ext import commands


class SoRGame(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.command(name="Schwarz oder Rot", aliases=["sor", "schwarz", "rot"], pass_context=True)
    async def create_game(self, ctx: commands.Context):
        msg = await ctx.send(
            embed=discord.Embed(
                title="Schwarz oder Rot",
                description=f"{ctx.author.mention} will Schwarz oder Rot spielen, @everyone macht mit!",
                color=var.C_RED,
            )
        )

        def check(reaction, user):
            return user != self.bot.user and reaction.message == msg

        await msg.add_reaction("🍻")
        await self.bot.wait_for("reaction_add", check=check)
        self.bot.add_listener
        await ctx.send("success")


def setup(bot: commands.Bot):
    bot.add_cog(SoRGame(bot))
