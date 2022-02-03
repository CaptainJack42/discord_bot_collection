from dataclasses import dataclass
from typing import Callable

import discord
import misc.variables as var
import plugins.ressource.card_deck as card_deck
from discord.ext import commands
from misc.bot_logger import get_logger


class SoRGameClient(commands.Cog):
    @dataclass
    class SoRPhase:
        message: str
        possible_reactions: list[str]
        parser: Callable

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.logger = get_logger()
        self.players: dict[discord.User, SoRPlayer] = dict()
        self.is_running: bool = False
        self.GAME_PHASES: list[self.SoRPhase] = [
            self.SoRPhase(  # noblack
                message="**Schwarz oder Rot?",  # noblack
                possible_reactions=["⚫", "🔴"],  # noblack
                parser=self.parse_schwarz_rot,  # noblack
            ),
            self.SoRPhase(
                message="**Höher, Tiefer oder Gleich als die erste Karte?**",
                possible_reactions=["⏫", "⏬", "🌗"],
                parser=self.parse_hoeher_tiefer,
            ),
            self.SoRPhase(
                message="**Innerhalb oder Außerhalb der ersten beiden Karten?** \n\
                ✅ : innerhalb \n\
                ❌ : außerhalb \n\
                🌗 : gleich",
                possible_reactions=["✅", "❌", "🌗"],
                parser=self.parse_inner_auserhalb,
            ),
            self.SoRPhase(
                message="**Hast du die Farbe bereits oder hast du sie nicht?** \n\
                ✅ : hab ich \n\
                ❌ : hab ich nicht",
                possible_reactions=["✅", "❌"],
                parser=self.parse_haben_nicht_haben,
            ),
        ]

    @commands.command(name="Schwarz oder Rot", aliases=["sor", "schwarz", "rot"], pass_context=True)
    async def create_game(self, ctx: commands.Context):
        if self.is_running:
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Es läuft bereits ein Spiel, beendet zuerst das laufende Spiel (mit `{var.PREFIX}stop`)",
                    color=var.C_RED,
                )
            )
            return
        msg = await ctx.send(
            f"{ctx.author.mention} will Schwarz oder Rot spielen, @everyone macht mit indem ihr auf :beers: klickt!"
        )

        self.is_running = True

        def check(reaction: discord.Reaction, user: discord.User):
            return user != self.bot.user and reaction.message == msg

        await msg.add_reaction("🍻")
        await msg.add_reaction("⏭️")
        reaction, user = await self.bot.wait_for("reaction_add", check=check)
        while str(reaction.emoji) != "⏭️":
            await self.add_player(user, ctx)
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
        await ctx.send("success")

    @commands.command(name="stop", aliases=["ende", "end"], pass_context=True)
    async def stop_game(self, ctx: commands.Context = None):
        # self.game = None
        # if ctx == None:
        #     self.logger.info("Game ended by timeout of all players")
        #     await self.game_channel.send("Das Spiel wurde beendet weil alle Spieler nicht reagiert haben.")
        # else:
        self.is_running = False
        self.logger.info(f"{ctx.author} ended the game")
        await ctx.send(f"{ctx.author.mention} hat das Spiel beendet")

    async def add_player(self, user: discord.User, ctx: commands.Context):
        if self.players.get(user) == None:
            player = SoRPlayer(list())
            self.players[user] = player
            await ctx.send(f"{user.mention} macht mit")
            self.logger.debug(f"{user} joined the game")

    async def send_msg_and_wait_reaction(self, msg: str, user: discord.User, viable_reacts: list[str]) -> str | None:
        pass

    async def run(self):
        for phase in self.GAME_PHASES:
            for player, player_attrs in self.players.items():
                msg = f"{player.mention} \n\
                    {phase.message}\n"
                if len(player_attrs.prev_cards) > 0:
                    msg += "Deine bisherigen Karten sind:"
                    for card in player_attrs.prev_cards:
                        msg += f"\n- **{card_deck.CardDeck.CARD_VALUE_MAP.get(card.value)}\
                            :{card.color._name_.lower()}: ({card.color._name_})**"

    async def parse_schwarz_rot(self, card: card_deck.Card, prev_cards: list[card_deck.Card]):
        pass

    async def parse_hoeher_tiefer(self, card: card_deck.Card, prev_cards: list[card_deck.Card]):
        pass

    async def parse_inner_auserhalb(self, card: card_deck.Card, prev_cards: list[card_deck.Card]):
        pass

    async def parse_haben_nicht_haben(self, card: card_deck.Card, prev_cards: list[card_deck.Card]):
        pass


@dataclass
class SoRPlayer:
    """dataclass representing a player. Can be expanded in the future to hold things like amount drank and so on."""

    prev_cards: list[card_deck.Card]


def setup(bot: commands.Bot):
    bot.add_cog(SoRGameClient(bot))
