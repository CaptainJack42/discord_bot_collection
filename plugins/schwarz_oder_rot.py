from dataclasses import dataclass, field
from enum import IntEnum
from random import randint
from typing import Callable

import discord
import misc.variables as var
from discord.ext import commands
from misc.bot_logger import get_logger


class SoRGameClient(commands.Cog):
    @dataclass
    class SoRPhase:
        message: str
        possible_reactions: list[str]
        runner: Callable

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.logger = get_logger()
        self.players: dict[discord.User, SoRPlayer] = dict()
        self.is_running: bool = False
        self.GAME_PHASES: dict[int, self.SoRPhase] = {
            0: self.SoRPhase(  # noblack
                message="**Schwarz oder Rot?",  # noblack
                possible_reactions=["⚫", "🔴"],  # noblack
                runner=self.phase_1,  # noblack
            ),
            1: self.SoRPhase(
                message="**Höher, Tiefer oder Gleich als die erste Karte?**",
                possible_reactions=["⏫", "⏬", "🌗"],
                runner=self.phase_2,
            ),
            2: self.SoRPhase(
                message="**Innerhalb oder Außerhalb der ersten beiden Karten?** \n\
                    ✅ : innerhalb \n\
                    ❌ : außerhalb \n\
                    🌗 : gleich",
                possible_reactions=["✅", "❌", "🌗"],
                runner=self.phase_3,
            ),
            3: self.SoRPhase(
                message="**Hast du die Farbe bereits oder hast du sie nicht?** \n\
                    ✅ : hab ich \n\
                    ❌ : hab ich nicht",
                possible_reactions=["✅", "❌"],
                runner=self.phase_4,
            ),
        }

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
            embed=discord.Embed(
                title="Schwarz oder Rot",
                description=f"{ctx.author.mention} will Schwarz oder Rot spielen, @everyone macht mit!",
                color=var.C_RED,
            )
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

    async def phase_1(self):
        pass

    async def phase_2(self):
        pass

    async def phase_3(self):
        pass

    async def phase_4(self):
        pass


class CardColor(IntEnum):
    HEARTS = 0
    DIAMONDS = 1
    SPADES = 2
    CLUBS = 3


@dataclass(order=True)
class Card:
    sort_index: int = field(init=False, repr=False)

    color: CardColor
    value: int

    def __post_init__(self):
        self.sort_index = self.value


class CardDeck:

    CARD_VALUE_MAP: dict = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Ace",
    }

    def __init__(self) -> None:
        self.__deck: list[Card] = list()
        for color in CardColor:
            for key in self.CARD_VALUE_MAP.keys():
                self.__deck.append(Card(color, key))

    def draw_card(self) -> Card:
        if len(self.__deck) == 0:
            return None
        rand: int = randint(0, len(self.__deck) - 1)
        return self.__deck.pop(rand)


@dataclass
class SoRPlayer:
    """dataclass representing a player. Can be expanded in the future to hold things like amount drank and so on."""

    prev_cards: list[Card]


def setup(bot: commands.Bot):
    bot.add_cog(SoRGameClient(bot))


if __name__ == "__main__":
    deck = CardDeck()
    card: Card = deck.draw_card()
    num_drawn: int = 0  # 0 because the last drawn card (None) is also counted
    while card != None:
        print(f"drew {deck.CARD_VALUE_MAP.get(card.value)} of {card.color._name_}")
        card = deck.draw_card()
        num_drawn += 1
    print(f"drew {num_drawn} cards in total")
