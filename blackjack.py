import random

# Define the card ranks, values, and suits
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Function to create a deck of cards
def create_deck():
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck

# Function to calculate the total value of a hand
def calculate_hand_value(hand):
    value = sum(values[card[0]] for card in hand)
    # Adjust for Aces if the total value is over 21
    num_aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

# Function to display a player's hand
def display_hand(hand, player_name):
    print(f"{player_name}'s Hand:")
    for card in hand:
        print(f"{card[0]} of {card[1]}")
    print(f"Total Value: {calculate_hand_value(hand)}\n")

# Function to play the blackjack game
def play_blackjack():
    print("Welcome to Blackjack!\n")

    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    display_hand(player_hand, "Player")
    display_hand(dealer_hand[-1:], "Dealer")

    # Player's turn
    while True:
        choice = input("Do you want to [H]it or [S]tand? ").lower()
        if choice == 'h':
            player_hand.append(deck.pop())
            display_hand(player_hand, "Player")
            if calculate_hand_value(player_hand) > 21:
                print("You busted! Dealer wins.")
                return
        elif choice == 's':
            break

    # Dealer's turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
        display_hand(dealer_hand, "Dealer")
        if calculate_hand_value(dealer_hand) > 21:
            print("Dealer busted! You win.")
            return

    # Compare hands
    player_score = calculate_hand_value(player_hand)
    dealer_score = calculate_hand_value(dealer_hand)
    if player_score > dealer_score:
        print("You win!")
    elif player_score < dealer_score:
        print("Dealer wins.")
    else:
        print("It's a tie!")

# Start the game
play_blackjack()
