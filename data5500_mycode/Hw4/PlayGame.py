from DeckOfCards import *

def calculate_score(hand):
    """Calculate blackjack score for a hand, accounting for Aces."""
    total = sum(card.value() for card in hand)
    aces = sum(1 for card in hand if card.rank == "Ace")

    # Adjust Ace from 11 -> 1 if needed
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def get_bet(balance):
    """Ask user for a bet and validate"""
    while True:
        try:
            bet = int(input(f"You have ${balance}. Enter your bet: "))
            if bet <= 0:
                print("Bet must be greater than 0!")
            elif bet > balance:
                print("You cannot bet more than your balance!")
            else:
                return bet
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_starting_balance():
    """Ask the player how much money they want to start with"""
    while True:
        try:
            amount = int(input("Enter your starting bankroll: $"))
            if amount <= 0:
                print("Bankroll must be greater than 0!")
            else:
                return amount
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    print("Welcome to Blackjack!\n")

    deck = DeckOfCards()
    balance = get_starting_balance()  # Player chooses bankroll

    while balance > 0:
        # Place bet
        bet = get_bet(balance)

        # Show deck before shuffle
        print("\nDeck before shuffle:")
        print(deck)
        deck.shuffle_deck()
        print("\nDeck after shuffle:")
        print(deck)

        # Initial deal
        user_hand = [deck.get_card(), deck.get_card()]
        dealer_hand = [deck.get_card(), deck.get_card()]

        user_score = calculate_score(user_hand)

        print("\nYour cards:", ', '.join(str(card) for card in user_hand), f"= {user_score}")
        print("Dealer shows:", dealer_hand[0])  # only show dealer’s first card here

        # Player's Turn
        while user_score < 21:
            hit = input("Do you want a hit? (y/n): ").lower()
            if hit == "y":
                user_hand.append(deck.get_card())
                user_score = calculate_score(user_hand)
                print("\nYour cards:", ', '.join(str(card) for card in user_hand), f"= {user_score}")
            else:
                break

        # If player busts
        if user_score > 21:
            print("You busted! Dealer wins.")
            balance -= bet
        else:
            # Dealer's Turn
            dealer_score = calculate_score(dealer_hand)
            print("\nDealer cards:", ', '.join(str(card) for card in dealer_hand), f"= {dealer_score}")

            while dealer_score < 17:
                dealer_hand.append(deck.get_card())
                dealer_score = calculate_score(dealer_hand)
                print("Dealer hits ->", ', '.join(str(card) for card in dealer_hand), f"= {dealer_score}")

            # Determine Outcome
            if dealer_score > 21:
                print("Dealer busts! You win!")
                balance += bet
            elif user_score > dealer_score:
                print("You win with higher score!")
                balance += bet
            elif dealer_score > user_score:
                print("Dealer wins with higher score.")
                balance -= bet
            else:
                print("Push (tie). Your bet is returned.")

        # Show player's balance
        print(f"\nYour balance: ${balance}")

        if balance <= 0:
            print("You are out of money! Game over.")
            break

        # Ask to replay
        play_again = input("\nPlay again? (y/n): ").lower()
        if play_again != "y":
            print(f"You leave the table with ${balance}.")
            break


if __name__ == "__main__":
    main()
