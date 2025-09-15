import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def value(self):
        """Return Blackjack value of the card."""
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        elif self.rank == "Ace":
            return 11  # Initially treats Ace as 11
        else:
            return int(self.rank)


class DeckOfCards:
    def __init__(self):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["Ace", "2", "3", "4", "5", "6", "7",
                      "8", "9", "10", "Jack", "Queen", "King"]
        self.deck = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def shuffle_deck(self):
        """Shuffle the deck of cards."""
        random.shuffle(self.deck)

    def get_card(self):
        """Deal the top card from the deck (pop index 0)."""
        if len(self.deck) == 0:
            print("Deck is empty, reshuffling...")
            self.__init__()  # Resets deck if empty
            self.shuffle_deck()
        return self.deck.pop(0)

    def __str__(self):
        """Print entire deck."""
        return ', '.join([str(card) for card in self.deck])