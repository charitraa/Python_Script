"""
This script allows a user to play a game of Rock, Paper, Scissors against the computer.
The user makes a choice, the computer makes a random choice, and the winner is determined
based on the classic rules of the game.
"""

import random

def get_user_choice():
    """
    Prompts the user to enter their choice (rock, paper, or scissors) and
    validates the input. Continues to prompt until a valid choice is entered.

    Returns:
        str: The user's valid choice, lowercased.
    """
    choices = ["rock", "paper", "scissors"]
    while True:
        user_input = input("Enter your choice (rock, paper, or scissors): ").lower()
        if user_input in choices:
            return user_input
        else:
            print("Invalid choice. Please choose from rock, paper, or scissors.")

def get_computer_choice():
    """
    Randomly selects a choice for the computer from rock, paper, or scissors.

    Returns:
        str: The computer's randomly selected choice.
    """
    choices = ["rock", "paper", "scissors"]
    return random.choice(choices)

def determine_winner(user_choice, computer_choice):
    """
    Determines the winner of the Rock, Paper, Scissors game based on the
    user's and computer's choices.

    Args:
        user_choice (str): The user's choice.
        computer_choice (str): The computer's choice.

    Returns:
        str: A message indicating the outcome of the game ('You win!',
             'Computer wins!', or 'It's a tie!').
    """
    print(f"\nYou chose: {user_choice}")
    print(f"Computer chose: {computer_choice}")

    if user_choice == computer_choice:
        return "It's a tie!"
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "paper" and computer_choice == "rock") or \
         (user_choice == "scissors" and computer_choice == "paper"):
        # Rock beats scissors, Paper beats rock, Scissors beats paper
        return "You win!"
    else:
        # In all other cases, the computer wins
        return "Computer wins!"

def play_game():
    """
    Runs a single round of the Rock, Paper, Scissors game.
    Orchestrates getting choices and determining the winner.
    """
    print("Welcome to Rock, Paper, Scissors!")
    print("---------------------------------\n")

    user_choice = get_user_choice()
    computer_choice = get_computer_choice()
    result = determine_winner(user_choice, computer_choice)

    print(f"\nResult: {result}")
    print("\nThanks for playing!")

if __name__ == "__main__":
    # This block ensures that play_game() is called only when the script
    # is executed directly, not when imported as a module.
    play_game()
