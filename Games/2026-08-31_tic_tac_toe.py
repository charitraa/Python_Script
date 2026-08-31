"""
A simple, console-based Tic Tac Toe game for two players.

Players take turns marking spaces on a 3x3 grid. The first player to get
three of their marks in a row (horizontally, vertically, or diagonally)
wins the game. If all nine squares are filled and no player has three
marks in a row, the game is a tie.
"""

def display_board(board):
    """
    Prints the Tic Tac Toe board to the console.

    The board is represented as a list of 9 strings.
    Indices 0-8 correspond to positions 1-9 on a standard keypad layout:
      1 | 2 | 3
      --+---+--
      4 | 5 | 6
      --+---+--
      7 | 8 | 9
    """
    print(f"\n {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} \n")

def player_input(board):
    """
    Prompts the current player for their next move and validates the input.

    Ensures the input is a number between 1-9 and the chosen spot is empty.
    Returns the chosen position (0-8) after validation.
    """
    while True:
        try:
            position = int(input("Enter your next move (1-9): "))
            # Adjust input to be 0-indexed for list access (0-8)
            position -= 1

            if not (0 <= position <= 8):
                print("Invalid input. Please enter a number between 1 and 9.")
            elif board[position] != ' ': # Check if the spot is already taken
                print("That spot is already taken! Choose another.")
            else:
                return position
        except ValueError: # Handle non-integer input
            print("Invalid input. Please enter a number.")

def place_mark(board, mark, position):
    """
    Places the player's mark ('X' or 'O') on the board at the given position.
    """
    board[position] = mark

def check_win(board, mark):
    """
    Checks if the given player (mark) has won the game.

    Checks all 3 rows, 3 columns, and 2 diagonals for a winning combination.
    """
    # Check rows
    if (board[0] == mark and board[1] == mark and board[2] == mark) or \
       (board[3] == mark and board[4] == mark and board[5] == mark) or \
       (board[6] == mark and board[7] == mark and board[8] == mark):
        return True
    # Check columns
    if (board[0] == mark and board[3] == mark and board[6] == mark) or \
       (board[1] == mark and board[4] == mark and board[7] == mark) or \
       (board[2] == mark and board[5] == mark and board[8] == mark):
        return True
    # Check diagonals
    if (board[0] == mark and board[4] == mark and board[8] == mark) or \
       (board[2] == mark and board[4] == mark and board[6] == mark):
        return True
    return False

def check_tie(board):
    """
    Checks if the game is a tie (all spots filled and no winner).
    A tie occurs if there are no empty spaces left on the board.
    """
    return ' ' not in board

def switch_player(current_player):
    """
    Switches the current player from 'X' to 'O' or vice-versa.
    """
    return 'O' if current_player == 'X' else 'X'

def play_game():
    """
    Main function to run the Tic Tac Toe game.
    Initializes the board, manages player turns, and checks for game end conditions.
    """
    # Initialize an empty board represented by a list of 9 empty strings
    board = [' '] * 9
    current_player = 'X' # 'X' typically starts
    game_over = False

    print("Welcome to Tic Tac Toe!")
    print("Player X goes first.")

    while not game_over:
        display_board(board) # Show the current state of the board
        print(f"It's {current_player}'s turn.")

        # Get a valid move from the current player
        position = player_input(board)

        # Place the player's mark on the board
        place_mark(board, current_player, position)

        # Check if the current player has won
        if check_win(board, current_player):
            display_board(board)
            print(f"\nCongratulations! Player {current_player} wins!")
            game_over = True
        # If not a win, check for a tie
        elif check_tie(board):
            display_board(board)
            print("\nIt's a tie!")
            game_over = True
        else:
            # If no win or tie, switch to the other player for the next turn
            current_player = switch_player(current_player)

    print("\nGame over. Thanks for playing!")

if __name__ == "__main__":
    # This block ensures play_game() only runs when the script is executed directly
    # (not when imported as a module).
    play_game()
