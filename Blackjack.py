import pygame
import requests
import os
import time
import random

pygame.init()
pygame.mixer.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
GREY = (169, 169, 169)

screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Blackjack")

def load_image(path, scale):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    except pygame.error as e:
        print(f"Unable to load image at path {path}: {e}")
        return pygame.Surface((100, 50))

lose_image = load_image("images/lose_popup.png", 0.1)
winner_image = load_image("images/winner_popup.png", 0.1)
lose_image_rect = lose_image.get_rect(center=(screen_width // 2, screen_height // 3))
winner_image_rect = winner_image.get_rect(center=(screen_width // 2, screen_height // 3))

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Unable to load sound at path {path}: {e}")
        return None

lose_sound = load_sound("sounds/lose_sound.mp3")
winner_sound = load_sound("sounds/winner_sound.wav")

font = pygame.font.Font(None, 28)

def draw_text(text, font, color, surface, x, y, centered=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if centered:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
suit_to_symbol = {'Hearts': 'H', 'Diamonds': 'D', 'Clubs': 'C', 'Spades': 'S'}

def create_shoe(num_decks=4):
    deck = [(rank, suit) for suit in suits for rank in ranks] * num_decks
    random.shuffle(deck)
    return deck

def calculate_hand_value(hand):
    value = sum(values[card[0]] for card in hand)
    num_aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

def display_hand(hand, x, y, max_width, max_height, num_cards):
    spacing = min(max_width // (num_cards + 1), max_width // 8)
    card_width = min(max_width // (num_cards + 2), max_width // 6)
    card_height = int(card_width * 1.4)
    start_x = x

    for index, card in enumerate(hand):
        card_img_path = os.path.join("images", f"{card[0]}{suit_to_symbol[card[1]]}.png")
        try:
            card_img = pygame.image.load(card_img_path)
            card_img = pygame.transform.scale(card_img, (card_width, card_height))
        except pygame.error as e:
            print(f"Unable to load image at path {card_img_path}: {e}")
            card_img = pygame.Surface((card_width, card_height))
            card_img.fill(RED)

        screen.blit(card_img, (start_x + index * spacing, y))

def button_clicked(button_rect, pos):
    return button_rect.collidepoint(pos)

def reset_game(deck):
    player_hand = []
    dealer_hand = []
    if len(deck) < 10:
        deck = create_shoe()
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    outcome_text = ""
    return player_hand, dealer_hand, deck, outcome_text

def animate_card_dealing(start_pos, end_pos, card_image, duration=0.5):
    start_time = time.time()
    while time.time() - start_time < duration:
        t = (time.time() - start_time) / duration
        current_pos = (start_pos[0] + t * (end_pos[0] - start_pos[0]), 
                       start_pos[1] + t * (end_pos[1] - start_pos[1]))
        screen.fill(GREEN)
        display_hand(player_hand, 50, 50, screen_width - 200, screen_height - 50, len(player_hand))
        display_hand(dealer_hand, 50, 250, screen_width - 200, screen_height - 50, len(dealer_hand))
        screen.blit(card_image, current_pos)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

score = 0

def determine_outcome(player_hand, dealer_hand):
    dealer_value = calculate_hand_value(dealer_hand)
    player_value = calculate_hand_value(player_hand)
    
    if player_value > 21:
        return "Bust! You lose!"
    elif dealer_value > 21:
        return "You win!"
    elif player_value > dealer_value:
        return "You win!"
    elif player_value < dealer_value:
        return "You lose!"
    else:
        return "It's a tie!"

def main():
    global screen, score, player_hand, dealer_hand
    running = True
    clock = pygame.time.Clock()
    deck = create_shoe()
    player_hand, dealer_hand, deck, outcome_text = reset_game(deck)
    
    hit_button_rect = pygame.Rect(screen_width - 170, 50, 120, 50)
    stand_button_rect = pygame.Rect(screen_width - 170, 110, 120, 50)
    restart_button_rect = pygame.Rect(screen_width - 170, 170, 120, 50)
    quit_button_rect = pygame.Rect(screen_width - 170, 230, 120, 50)
    fullscreen_button_rect = pygame.Rect(screen_width - 170, 290, 120, 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if button_clicked(hit_button_rect, pos) and not outcome_text:
                    response = requests.post('http://127.0.0.1:5000/deal_card')
                    if response.ok:
                        card = response.json().get('card')
                        if card:
                            card_image_path = os.path.join("images", f"{card}.png")
                            card_image = pygame.image.load(card_image_path)
                            animate_card_dealing((screen_width - 200, screen_height - 100), (50 + len(player_hand) * 30, 50), card_image)
                            player_hand.append((card[:-1], suit_to_symbol.get(card[-1])))
                            if calculate_hand_value(player_hand) > 21:
                                outcome_text = "Bust! You lose!"
                                score -= 1
                                if lose_sound:
                                    lose_sound.play()
                elif button_clicked(stand_button_rect, pos) and not outcome_text:
                    while calculate_hand_value(dealer_hand) < 17:
                        response = requests.post('http://127.0.0.1:5000/deal_card')
                        if response.ok:
                            card = response.json().get('card')
                            if card:
                                card_image_path = os.path.join("images", f"{card}.png")
                                card_image = pygame.image.load(card_image_path)
                                animate_card_dealing((screen_width - 200, screen_height - 100), (50 + len(dealer_hand) * 30, 250), card_image)
                                dealer_hand.append((card[:-1], suit_to_symbol.get(card[-1])))
                    outcome_text = determine_outcome(player_hand, dealer_hand)
                    if "win" in outcome_text.lower():
                        score += 1
                        if winner_sound:
                            winner_sound.play()
                    elif "lose" in outcome_text.lower():
                        score -= 1
                        if lose_sound:
                            lose_sound.play()
                elif button_clicked(restart_button_rect, pos):
                    player_hand, dealer_hand, deck, outcome_text = reset_game(deck)
                elif button_clicked(quit_button_rect, pos):
                    running = False
                elif button_clicked(fullscreen_button_rect, pos):
                    pygame.display.toggle_fullscreen()

        screen.fill(GREEN)
        display_hand(player_hand, 50, 50, screen_width - 200, screen_height - 50, len(player_hand))
        display_hand(dealer_hand, 50, 250, screen_width - 200, screen_height - 50, len(dealer_hand))

        pygame.draw.rect(screen, BLACK, hit_button_rect)
        draw_text("Hit", font, WHITE, screen, hit_button_rect.centerx, hit_button_rect.centery)
        pygame.draw.rect(screen, BLACK, stand_button_rect)
        draw_text("Stand", font, WHITE, screen, stand_button_rect.centerx, stand_button_rect.centery)
        pygame.draw.rect(screen, BLACK, restart_button_rect)
        draw_text("Restart", font, WHITE, screen, restart_button_rect.centerx, restart_button_rect.centery)
        pygame.draw.rect(screen, BLACK, quit_button_rect)
        draw_text("Quit", font, WHITE, screen, quit_button_rect.centerx, quit_button_rect.centery)
        pygame.draw.rect(screen, BLACK, fullscreen_button_rect)
        draw_text("Fullscreen", font, WHITE, screen, fullscreen_button_rect.centerx, fullscreen_button_rect.centery)

        draw_text(f"Score: {score}", font, WHITE, screen, screen_width - 100, 10)

        if outcome_text:
            draw_text(outcome_text, font, RED, screen, screen_width // 2, screen_height // 2)
            if "win" in outcome_text.lower():
                screen.blit(winner_image, winner_image_rect)
            else:
                screen.blit(lose_image, lose_image_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
