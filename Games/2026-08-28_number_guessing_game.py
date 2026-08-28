import random

"""
This script implements a simple number guessing game.

The computer picks a random number within a specified range, and the player
tries to guess it. The game provides hints (too high or too low) after
each guess and limits the number of attempts.
"""

def play_number_guessing_game():
    """
    Plays a round of the number guessing game.
    The player has a limited number of guesses to find a random number
    between a specified minimum and maximum value.
    """
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    print("You have 10 guesses to find it.")

    # Define the range for the random number
    secret_number_min = 1
    secret_number_max = 100
    # Define the maximum number of attempts allowed
    max_guesses = 10

    # Generate a random integer between secret_number_min and secret_number_max (inclusive)
    secret_number = random.randint(secret_number_min, secret_number_max)
    guesses_taken = 0 # Initialize a counter for guesses

    # Loop as long as the player has guesses remaining
    while guesses_taken < max_guesses:
        try:
            # Get player's guess input
            # The f-string formats the prompt to show current guess number and total allowed
            user_input = input(f"Guess {guesses_taken + 1}/{max_guesses}: Enter your guess: ")
            guess = int(user_input) # Convert the string input to an integer

            # Validate if the guess is within the allowed range
            if not (secret_number_min <= guess <= secret_number_max):
                print(f"Oops! Your guess must be between {secret_number_min} and {secret_number_max}. Try again.")
                # This input doesn't count as a guess, so we 'continue' to the next loop iteration
                # without incrementing guesses_taken.
                continue

            # If the input is a valid number and within range, it counts as a guess.
            guesses_taken += 1

            # Compare the guess to the secret number and provide feedback
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                # Player guessed correctly
                print(f"Congratulations! You guessed the number {secret_number} in {guesses_taken} guesses!")
                return # Exit the function as the game is over

        except ValueError:
            # Handle cases where the user input cannot be converted to an integer
            # (e.g., if they type "hello" instead of a number).
            print("Invalid input. Please enter a whole number.")
            # This invalid input doesn't count as a guess, so we 'continue'
            # without incrementing guesses_taken.
            continue

    # If the loop finishes, it means the player ran out of guesses
    print("\nGame Over!")
    print(f"You ran out of guesses. The number I was thinking of was {secret_number}.")

if __name__ == "__main__":
    # This block ensures that play_number_guessing_game() is called only when
    # the script is executed directly. It will not run if the script is
    # imported as a module into another Python file.
    play_number_guessing_game()
