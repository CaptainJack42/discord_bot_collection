from dataclasses import dataclass, field
from enum import IntEnum
from random import randint


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


if __name__ == "__main__":
    deck = CardDeck()
    card: Card = deck.draw_card()
    num_drawn: int = 0  # 0 because the last drawn card (None) is also counted
    while card != None:
        print(f"drew {deck.CARD_VALUE_MAP.get(card.value)} of {card.color._name_}")
        card = deck.draw_card()
        num_drawn += 1
    print(f"drew {num_drawn} cards in total")
