"""
This script implements a classic text-based Hangman game.

The player guesses letters to uncover a hidden word. They have a limited
number of incorrect guesses before the "hangman" is fully drawn and they lose.
"""

import random

# List of words for the game
WORD_LIST = [
    "python", "programming", "developer", "computer", "algorithm",
    "keyboard", "monitor", "application", "software", "hardware",
    "internet", "website", "framework", "database", "security",
    "function", "variable", "string", "integer", "boolean",
    "loop", "conditional", "library", "module", "project",
    "challenge", "solution", "iterate", "recursion", "encryption"
]

# Hangman ASCII art stages. Each string in the list represents a stage
# from 0 (no incorrect guesses) to 6 (game over).
HANGMAN_PICS = [
    # Stage 0: Initial empty gallows
    """
       -----
       |   |
           |
           |
           |
           |
    ---------
    """,
    # Stage 1: Head
    """
       -----
       |   |
       O   |
           |
           |
           |
    ---------
    """,
    # Stage 2: Body
    """
       -----
       |   |
       O   |
       |   |
           |
           |
    ---------
    """,
    # Stage 3: One arm
    """
       -----
       |   |
       O   |
      /|   |
           |
           |
    ---------
    """,
    # Stage 4: Both arms
    """
       -----
       |   |
       O   |
      /|\\  |
           |
           |
    ---------
    """,
    # Stage 5: One leg
    """
       -----
       |   |
       O   |
      /|\\  |
      /    |
           |
    ---------
    """,
    # Stage 6: Both legs - Game Over!
    """
       -----
       |   |
       O   |
      /|\\  |
      / \\  |
           |
    ---------
    """
]

def get_word():
    """
    Selects a random word from the WORD_LIST.
    The word is converted to uppercase for consistent letter handling.
    """
    return random.choice(WORD_LIST).upper()

def display_game_status(hangman_stage, guessed_word_display, all_guessed_letters, attempts_left):
    """
    Prints the current game status to the console.
    This includes:
    - The current hangman ASCII art (based on `hangman_stage`).
    - The hidden word's current state (e.g., H _ L L _ ).
    - A list of all letters the player has guessed so far.
    - The number of attempts remaining.
    """
    print("\n" + "="*40)
    print(HANGMAN_PICS[hangman_stage]) # Display the hangman drawing corresponding to the current incorrect guess count
    print(f"Word: {guessed_word_display}") # Show the word with unguessed letters as underscores
    
    # Display all guessed letters, sorted alphabetically for readability
    print(f"Guessed letters: {' '.join(sorted(list(all_guessed_letters)))}")
    print(f"Attempts left: {attempts_left}")
    print("="*40)

def play_hangman():
    """
    Main function to run the Hangman game.
    Initializes game variables, handles the game loop, user input,
    guess processing, and checks for win/loss conditions.
    """
    word_to_guess = get_word() # Select a word for the current game
    all_guessed_letters = set() # A set to store all letters the player has guessed (correct and incorrect)
    incorrect_guesses_count = 0 # Counter for incorrect guesses
    
    # The maximum number of incorrect attempts allowed.
    # It's one less than the total number of HANGMAN_PICS stages,
    # because stage 0 represents 0 incorrect guesses.
    max_attempts = len(HANGMAN_PICS) - 1

    print("Welcome to Hangman!")
    print(f"Try to guess the {len(word_to_guess)}-letter word.")

    # Main game loop: continues as long as the player has attempts left
    # and hasn't guessed the entire word.
    while incorrect_guesses_count < max_attempts:
        # Generate the current display of the word.
        # Letters already guessed correctly are shown, others are underscores.
        current_word_display = ""
        for letter in word_to_guess:
            if letter in all_guessed_letters:
                current_word_display += letter + " "
            else:
                current_word_display += "_ "

        # Check if the player has won BEFORE asking for a new guess.
        # If there are no underscores, the word is fully guessed.
        if "_" not in current_word_display:
            display_game_status(incorrect_guesses_count, current_word_display, all_guessed_letters, max_attempts - incorrect_guesses_count)
            print(f"\nCONGRATULATIONS! You guessed the word: {word_to_guess}!")
            return # End the game

        # Display the current state of the game to the player
        display_game_status(incorrect_guesses_count, current_word_display, all_guessed_letters, max_attempts - incorrect_guesses_count)

        # Get player's guess
        guess = input("Guess a letter: ").upper() # Convert input to uppercase for case-insensitive checking

        # --- Input Validation ---
        # 1. Check if the input is a single alphabet character
        if not guess.isalpha() or len(guess) != 1:
            print("Invalid input. Please enter a single letter (A-Z).")
            continue # Skip to the next loop iteration to ask for input again
        
        # 2. Check if the letter has already been guessed
        if guess in all_guessed_letters:
            print(f"You already guessed '{guess}'. Try a different letter.")
            continue # Skip to the next loop iteration

        # Add the valid, new guess to the set of all guessed letters
        all_guessed_letters.add(guess)

        # --- Process the Guess ---
        if guess in word_to_guess:
            print(f"Good guess! '{guess}' is in the word.")
        else:
            print(f"Sorry, '{guess}' is not in the word.")
            incorrect_guesses_count += 1 # Increment incorrect guess counter

    # --- Game Over Condition (Player ran out of attempts) ---
    # After the loop finishes, if the player hasn't won, it means they lost.
    # Display the final game status with the last hangman stage.
    current_word_display = "" # Re-generate for the final display if player loses without fully guessing
    for letter in word_to_guess:
        if letter in all_guessed_letters:
            current_word_display += letter + " "
        else:
            current_word_display += "_ " # Still show underscores for unguessed letters if game over by attempts

    display_game_status(incorrect_guesses_count, current_word_display, all_guessed_letters, max_attempts - incorrect_guesses_count)
    print("\nGAME OVER! You ran out of attempts.")
    print(f"The word was: {word_to_guess}")

# This block ensures that play_hangman() is called only when the script is executed directly
# (not when imported as a module into another script).
if __name__ == "__main__":
    play_hangman()
