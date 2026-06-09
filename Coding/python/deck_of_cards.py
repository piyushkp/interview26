"""Deck of cards (object-oriented design exercise).

Port of java/DeckOfCards.java (original package code.ds), which models a generic
Deck<T extends Card>, an abstract Card, a Suit enum and a Hand<T>.

The Java file has no concrete Card subclass and no main; a SimpleCard subclass
and a small demo are added here so the module is runnable.

NOTE: Deck.shuffle is ported faithfully and is effectively a no-op: Java computes
`(int) Math.random() % (i + 1)`, and `(int)` of a value in [0, 1) is always 0, so
every swap index j is 0.
"""

from __future__ import annotations

import enum
import random
from typing import List, Optional


class Suit(enum.Enum):
    CLUB = 0
    DIAMOND = 1
    HEART = 2
    SPADE = 3

    @staticmethod
    def get_suit_from_value(value: int) -> Optional["Suit"]:
        for s in Suit:
            if s.value == value:
                return s
        return None


class Card:
    """Abstract card; subclasses must implement value()."""

    def __init__(self, c: int, s: Suit):
        self._available = True
        # number/face on the card: 2-10, 11 = Jack, 12 = Queen, 13 = King, 1 = Ace.
        self.face_value = c
        self.suit_ = s

    def value(self) -> int:
        raise NotImplementedError("abstract method: value()")

    def suit(self) -> Suit:
        return self.suit_

    def is_available(self) -> bool:
        """Whether the card is available to be given out to someone."""
        return self._available

    def mark_unavailable(self) -> None:
        self._available = False

    def mark_available(self) -> None:
        self._available = True

    def print_card(self) -> None:
        face_values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                       "J", "Q", "K"]
        out = face_values[self.face_value - 1]
        if self.suit_ == Suit.CLUB:
            out += "c"
        elif self.suit_ == Suit.HEART:
            out += "h"
        elif self.suit_ == Suit.DIAMOND:
            out += "d"
        elif self.suit_ == Suit.SPADE:
            out += "s"
        print(out + " ", end="")


class SimpleCard(Card):
    """Concrete Card whose value is just its face value (added for the demo)."""

    def value(self) -> int:
        return self.face_value


class Deck:
    """A generic deck of cards."""

    def __init__(self):
        self.cards: List[Card] = []
        self.dealt_index = 0  # marks first undealt card

    def set_deck_of_cards(self, deck_of_cards: List[Card]) -> None:
        self.cards = deck_of_cards

    def shuffle(self) -> None:
        # Faithful port: j is always 0 (see the module docstring), so this just
        # repeatedly swaps cards[i] with cards[0].
        for i in range(len(self.cards) - 1, 0, -1):
            j = int(random.random()) % (i + 1)
            card1 = self.cards[i]
            card2 = self.cards[j]
            self.cards[i] = card2
            self.cards[j] = card1

    def remaining_cards(self) -> int:
        return len(self.cards) - self.dealt_index

    def deal_hand(self, number: int) -> Optional[List[Optional[Card]]]:
        if self.remaining_cards() < number:
            return None
        hand: List[Optional[Card]] = [None] * number
        count = 0
        while count < number:
            card = self.deal_card()
            if card is not None:
                hand[count] = card
                count += 1
        return hand

    def deal_card(self) -> Optional[Card]:
        if self.remaining_cards() == 0:
            return None
        card = self.cards[self.dealt_index]
        card.mark_unavailable()
        self.dealt_index += 1
        return card

    def print_deck(self) -> None:
        for card in self.cards:
            card.print_card()


class Hand:
    """A hand of cards with a simple additive score."""

    def __init__(self):
        self.cards: List[Card] = []

    def score(self) -> int:
        return sum(card.value() for card in self.cards)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def print_hand(self) -> None:
        for card in self.cards:
            card.print_card()


if __name__ == "__main__":
    # Build a standard 52-card deck (faces 1..13 in each suit).
    all_cards: List[Card] = []
    for s in Suit:
        for face in range(1, 14):
            all_cards.append(SimpleCard(face, s))

    deck = Deck()
    deck.set_deck_of_cards(all_cards)
    deck.shuffle()  # faithful no-op shuffle
    print("Remaining cards:", deck.remaining_cards())

    hand = Hand()
    hand.add_card(SimpleCard(3, Suit.HEART))
    hand.add_card(SimpleCard(4, Suit.SPADE))
    print("Hand: ", end="")
    hand.print_hand()
    print()
    print("Score:", hand.score())

    dealt = deck.deal_hand(5)
    print("Dealt 5 cards: ", end="")
    if dealt:
        for c in dealt:
            if c is not None:
                c.print_card()
    print()
