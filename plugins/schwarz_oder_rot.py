import asyncio
from dataclasses import dataclass
from typing import Callable

import discord
import misc.variables as var
import plugins.ressource.card_deck as card_deck
from discord.ext import commands
from misc.bot_logger import get_logger


class SoRGameClient(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.logger = get_logger()
        self.games: dict[discord.TextChannel, SoRGame] = dict()

    @commands.command(name="Schwarz oder Rot", aliases=["sor", "schwarz", "rot"], pass_context=True)
    async def create_game(self, ctx: commands.Context):
        if ctx.channel in self.games.keys():
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Es läuft bereits ein Spiel in diesem Channel, beendet zuerst das laufende Spiel (mit `{var.PREFIX}stop`)",
                    color=var.C_RED,
                )
            )
            return

        new_game = SoRGame(self.bot, ctx)
        self.games[ctx.channel] = new_game
        await new_game.create_game()

    @commands.command(name="stop", aliases=["ende", "end"])
    async def stop_game(self, ctx: commands.Context):
        if ctx.channel in self.games.keys():
            stopped_game = self.games.pop(ctx.channel)
            stopped_game.is_running = False
            del stopped_game
            await ctx.send(f"{ctx.author.mention} hat das Spiel in {ctx.channel.mention} beendet.")


class SoRGame:
    @dataclass
    class SoRPlayer:
        """dataclass representing a player. Can be expanded in the future to hold things like amount drank and so on."""

        prev_cards: list[card_deck.Card]
        is_active: bool = True

    @dataclass
    class SoRPhase:
        message: str
        possible_reactions: list[str]
        parser: Callable

    def __init__(self, bot: commands.Bot, channel: commands.Context) -> None:
        self.bot = bot
        self.game_channel: commands.Context = channel
        self.logger = get_logger()
        self.players: dict[discord.User, self.SoRPlayer] = dict()
        self.is_running: bool = True
        self.GAME_PHASES: list[self.SoRPhase] = [
            self.SoRPhase(  # noblack
                message="**⚫Schwarz⚫ oder 🔴Rot🔴?**",  # noblack
                possible_reactions=["⚫", "🔴"],  # noblack
                parser=self.parse_schwarz_rot,  # noblack
            ),
            self.SoRPhase(
                message="**⏫Höher⏫, ⏬Tiefer⏬ oder 🌗Gleich🌗 als die erste Karte?**",
                possible_reactions=["⏫", "⏬", "🌗"],
                parser=self.parse_hoeher_tiefer,
            ),
            self.SoRPhase(
                message="**✅Innerhalb✅, ❌Außerhalb❌ oder 🌗gleich🌗 der ersten beiden Karten?** \n",
                possible_reactions=["✅", "❌", "🌗"],
                parser=self.parse_inner_auserhalb,
            ),
            self.SoRPhase(
                message="**✅Hast du die Farbe bereits✅ oder ❌hast du sie nicht❌?** \n",
                possible_reactions=["✅", "❌"],
                parser=self.parse_haben_nicht_haben,
            ),
        ]

    async def create_game(self):
        msg = await self.game_channel.send(
            f"{self.game_channel.author.mention} will Schwarz oder Rot spielen, @everyone macht mit indem ihr auf :beers: klickt!"
        )

        def check(reaction: discord.Reaction, user: discord.User):
            return user != self.bot.user and reaction.message == msg

        await msg.add_reaction("🍻")
        await msg.add_reaction("⏭️")
        reaction, user = await self.bot.wait_for("reaction_add", check=check)
        while str(reaction.emoji) != "⏭️":
            await self.add_player(user)
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
        if not self.players.get(user):
            await self.add_player(user)
        await self.run()

    async def add_player(self, user: discord.User):
        if self.players.get(user) == None:
            player = self.SoRPlayer(list())
            self.players[user] = player
            await self.game_channel.send(f"{user.mention} macht mit")
            self.logger.debug(f"{user} joined the game")

    async def remove_player(self, user: discord.User):
        if user in self.players.keys():
            self.players[user].is_active = False

    async def send_msg_and_wait_reaction(
        self, msg: str, curr_player: discord.User, viable_reacts: list[str]
    ) -> str | None:
        message: discord.Message = await self.game_channel.send(msg)
        for emoji in viable_reacts:
            await message.add_reaction(emoji)

        def check(reaction: discord.Reaction, user: discord.User):
            return user == curr_player and str(reaction.emoji) in viable_reacts and reaction.message == message

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=120.0, check=check)
        except asyncio.TimeoutError:
            # await self.game_channel.send(
            #     f"{curr_player.mention} hat nicht reagiert und wird nun aus dem Spiel entfernt."
            # )
            return None
        else:
            return str(reaction)

    async def run(self):
        deck = card_deck.CardDeck()
        for phase in self.GAME_PHASES:
            for player, player_attrs in self.players.items():
                if not player_attrs.is_active:
                    continue
                msg = f"{player.mention} \n{phase.message}\n"
                if len(player_attrs.prev_cards) > 0:
                    msg += "Deine bisherigen Karten sind:"
                    for card in player_attrs.prev_cards:
                        msg += f"\n- **{deck.CARD_VALUE_MAP.get(card.value)}:{card.color._name_.lower()}: ({deck.CARD_VALUE_MAP.get(card.value)} of {card.color._name_})**"

                reaction = await self.send_msg_and_wait_reaction(msg, player, phase.possible_reactions)

                if not self.is_running:
                    """
                    prevents the game from sending timeout messages or still being playable after {var.PREFIX}stop was called.
                    """
                    return

                if reaction == None:
                    await self.remove_player(player)
                    active_players: int = 0
                    for p in self.players.values():
                        if p.is_active:
                            active_players += 1
                            break
                    if active_players <= 0:
                        await self.game_channel.send("Das Spiel wurde beendet weil keine Spieler mehr übrig sind")
                        self.game_channel.author = player
                        self.logger.info("Game ended by timeout of all players")
                        # self.clear_game_info_vars()  # No Players left
                        return
                    continue  # Player timed out

                self.logger.debug(
                    f"{player.name} reacted with {reaction} to {phase.message}."
                    f"This is viable -> {str(reaction) in phase.possible_reactions}"
                )

                card: card_deck.Card = deck.draw_card()

                msg = (
                    f"{player.mention}\n"
                    f"deine Karte ist: **{deck.CARD_VALUE_MAP.get(card.value)}:{card.color._name_.lower()}: ({deck.CARD_VALUE_MAP.get(card.value)} of {card.color._name_})**"
                )

                if await phase.parser(card, player_attrs.prev_cards, reaction):
                    msg += "\n**RICHTIG!** Wähle jemanden der trinkt!"
                else:
                    msg += "\n**FALSCH!** Trink!"

                player_attrs.prev_cards.append(card)

                try:
                    await self.game_channel.send(msg)
                except AttributeError:
                    # self.clear_game_info_vars()  # game has ended (was stopped by {var.PREFIX}stop)
                    return

        await self.game_channel.send(f"Das Spiel ist vorbei, startet ein neues mit `{var.PREFIX}sor`")

        # self.clear_game_info_vars()

    async def parse_schwarz_rot(self, card: card_deck.Card, prev_cards: list[card_deck.Card], reaction: str) -> bool:
        if reaction == "⚫":
            if card.color == card_deck.CardColor.SPADES or card.color == card_deck.CardColor.CLUBS:
                return True
            else:
                return False
        elif reaction == "🔴":
            if card.color == card_deck.CardColor.HEARTS or card.color == card_deck.CardColor.DIAMONDS:
                return True
            else:
                return False

    async def parse_hoeher_tiefer(self, card: card_deck.Card, prev_cards: list[card_deck.Card], reaction: str) -> bool:
        if reaction == "⏫":
            if card.value > prev_cards[0].value:
                return True
            else:
                return False
        elif reaction == "⏬":
            if card.value < prev_cards[0].value:
                return True
            else:
                return False
        elif reaction == "🌗":
            if card.value == prev_cards[0].value:
                return True
            else:
                return False

    async def parse_inner_auserhalb(
        self, card: card_deck.Card, prev_cards: list[card_deck.Card], reaction: str
    ) -> bool:
        if reaction == "✅":
            if card.value > min(prev_cards[0:]).value and card.value < max(prev_cards[0:]).value:
                return True
            else:
                return False
        if reaction == "❌":
            if card.value < min(prev_cards[0:]).value or card.value > max(prev_cards[0:]).value:
                return True
            else:
                return False
        if reaction == "🌗":
            for c in prev_cards:
                if card.value == c.value:
                    return True
            return False

    async def parse_haben_nicht_haben(
        self, card: card_deck.Card, prev_cards: list[card_deck.Card], reaction: str
    ) -> bool:
        if reaction == "✅":
            for c in prev_cards:
                if card.color == c.color:
                    return True
            return False
        elif reaction == "❌":
            for c in prev_cards:
                if card.color == c.color:
                    return False
            return True


def setup(bot: commands.Bot):
    bot.add_cog(SoRGameClient(bot))
