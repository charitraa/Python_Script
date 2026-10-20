"""
A beginner-friendly console-based Memory Card Game.

Players flip two cards at a time, trying to find matching pairs.
If cards match, they stay face-up. If not, they flip back face-down
after a short delay. The game ends when all pairs are found,
and the script reports the number of turns taken.
"""

import random
import time
import os
import platform

# --- Configuration Constants ---
BOARD_ROWS = 4
BOARD_COLS = 4
# Emojis for the card values. We need (BOARD_ROWS * BOARD_COLS) / 2 unique pairs.
CARD_VALUES = ['🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🍑', '🍍',
               '🥝', '🥥', '🥭', '🍐', '🫐', '🍈', '🌶️', '🍆']
# Ensure we have enough card values for the board size
REQUIRED_PAIRS = (BOARD_ROWS * BOARD_COLS) // 2
if len(CARD_VALUES) < REQUIRED_PAIRS:
    raise ValueError(f"Not enough unique CARD_VALUES for a {BOARD_ROWS}x{BOARD_COLS} board. "
                     f"Need {REQUIRED_PAIRS} unique values, have {len(CARD_VALUES)}.")
CARD_VALUES = CARD_VALUES[:REQUIRED_PAIRS] # Trim to exact required number

HIDDEN_CARD_SYMBOL = '?' # Symbol to display for hidden cards

# --- Utility Functions ---

def clear_screen():
    """Clears the console screen."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        # For Unix-like systems (Linux, macOS) or a generic fallback
        os.system('clear')
        # A simpler, more cross-platform "clear" if os.system is problematic:
        # print('\n' * 50) 

def create_board():
    """
    Creates a new game board with shuffled pairs of cards.
    Returns:
        tuple: A tuple containing:
            - board (list of list of str): The actual card values on the board.
            - revealed (list of list of bool): A parallel board tracking which cards are revealed.
    """
    # Create a list of all card values, with each appearing twice
    all_cards = CARD_VALUES * 2
    random.shuffle(all_cards) # Shuffle them randomly

    board = []
    revealed = []
    for r in range(BOARD_ROWS):
        row_cards = []
        row_revealed = []
        for c in range(BOARD_COLS):
            # Pop a card from the shuffled list to fill the board
            row_cards.append(all_cards.pop())
            row_revealed.append(False) # All cards start as hidden
        board.append(row_cards)
        revealed.append(row_revealed)
    return board, revealed

def display_board(board, revealed, turns_taken):
    """
    Prints the current state of the game board to the console.

    Args:
        board (list of list of str): The actual card values.
        revealed (list of list of bool): Tracks which cards are currently face-up.
        turns_taken (int): The number of turns the player has taken.
    """
    print("--- Memory Card Game ---")
    print(f"Turns: {turns_taken}\n")

    # Print column headers (0, 1, 2, ...)
    print("   ", end="")
    for col in range(BOARD_COLS):
        print(f" {col} ", end="")
    print("\n  " + "---" * BOARD_COLS) # Separator line

    # Print board rows
    for r in range(BOARD_ROWS):
        print(f"{r} |", end="") # Print row header (0, 1, 2, ...)
        for c in range(BOARD_COLS):
            if revealed[r][c]:
                print(f" {board[r][c]} ", end="") # Show card value if revealed
            else:
                print(f" {HIDDEN_CARD_SYMBOL} ", end="") # Show hidden symbol otherwise
        print("|")
    print("  " + "---" * BOARD_COLS) # Bottom separator

def get_card_coordinates(board_size, revealed_cards, prompt_msg, exclude_coords=None):
    """
    Prompts the player to enter card coordinates and validates the input.

    Args:
        board_size (tuple): (rows, cols) of the board.
        revealed_cards (list of list of bool): Current state of revealed cards.
        prompt_msg (str): Message to display to the user.
        exclude_coords (tuple, optional): (row, col) to prevent the user from selecting again.
                                           Used for the second card selection.

    Returns:
        tuple: (row, col) of the selected card, or None if input is invalid.
    """
    max_row, max_col = board_size
    while True:
        try:
            user_input = input(prompt_msg).strip()
            row, col = map(int, user_input.split())

            # Validate coordinates are within board bounds
            if not (0 <= row < max_row and 0 <= col < max_col):
                print(f"Invalid input: Row must be 0-{max_row-1} and Column 0-{max_col-1}.")
            # Check if the card is already revealed (i.e., already matched)
            elif revealed_cards[row][col]:
                print("Invalid input: This card is already matched.")
            # Check if the user selected the same card twice for the second pick
            elif exclude_coords and (row, col) == exclude_coords:
                print("Invalid input: You cannot select the same card twice. Choose a different one.")
            else:
                return row, col
        except ValueError:
            print("Invalid input: Please enter two numbers separated by a space (e.g., '0 1').")
        except IndexError: # Catches cases like "0" with no space
            print("Invalid input: Please enter two numbers separated by a space (e.g., '0 1').")

def main_game():
    """
    Main function to run the Memory Card Game.
    """
    board, revealed = create_board()
    
    total_pairs = (BOARD_ROWS * BOARD_COLS) // 2
    matched_pairs = 0
    turns = 0

    while matched_pairs < total_pairs:
        clear_screen()
        display_board(board, revealed, turns)

        # --- First Card Selection ---
        print("\nSelect your first card.")
        print("Enter row and column (e.g., '0 0' for top-left card).")
        r1, c1 = get_card_coordinates((BOARD_ROWS, BOARD_COLS), revealed, "First card (row col): ")

        # Temporarily reveal the first chosen card
        revealed[r1][c1] = True
        
        clear_screen()
        display_board(board, revealed, turns)
        
        # --- Second Card Selection ---
        print("\nSelect your second card.")
        print("Enter row and column (e.g., '0 0' for top-left card).")
        # Pass the first card's coordinates to prevent selecting it again
        r2, c2 = get_card_coordinates((BOARD_ROWS, BOARD_COLS), revealed, "Second card (row col): ", (r1, c1))

        # Temporarily reveal the second chosen card
        revealed[r2][c2] = True
        
        clear_screen()
        display_board(board, revealed, turns)
        
        turns += 1
        
        # --- Check for Match ---
        if board[r1][c1] == board[r2][c2]:
            print("🎉 It's a match! 🎉")
            matched_pairs += 1
            # Cards stay revealed, no need to change `revealed[r][c]` back to False
        else:
            print("😔 No match. Cards will flip back.")
            # Cards flip back after a delay
            revealed[r1][c1] = False
            revealed[r2][c2] = False
        
        time.sleep(2) # Pause for a moment to let the player see the result

    # --- Game End ---
    clear_screen()
    display_board(board, revealed, turns) # Show final state
    print("\n-------------------------------------")
    print("🌟 Congratulations! All pairs found! 🌟")
    print(f"You completed the game in {turns} turns.")
    print("-------------------------------------")

if __name__ == "__main__":
    main_game()
