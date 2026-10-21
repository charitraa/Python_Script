import os
import random
import time
import sys

# Platform-specific imports for non-blocking input
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-like (Linux, macOS)
    import termios
    import tty
    import select # Used with sys.stdin for non-blocking read

"""
A simple console-based Snake game.

Players control a snake that moves around a bounded board, eating food to grow
and score points. The game ends if the snake collides with the walls or its
own body. The game features non-blocking input for a real-time experience
and adapts to both Windows and Unix-like operating systems.

Controls:
- 'W', 'A', 'S', 'D' to change snake direction (Up, Left, Down, Right).
- 'Q' to quit the game.
- 'R' to restart the game after it ends.
"""

# --- Constants ---
BOARD_WIDTH = 40
BOARD_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
INITIAL_GAME_SPEED = 0.15 # Seconds per frame (lower value means faster game)

# Character representations for drawing
HEAD_CHAR = 'O'
BODY_CHAR = 'o'
FOOD_CHAR = '@'
WALL_CHAR = '#'
EMPTY_CHAR = ' '

# Directions as (dx, dy) tuples
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    """
    Manages the state and logic of the console Snake game.
    """

    def __init__(self):
        """
        Initializes the game, setting up the board, snake, food, score,
        and terminal settings for non-blocking input.
        """
        self.snake = []
        self.food = None
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.speed = INITIAL_GAME_SPEED

        # Store original terminal settings for Unix-like systems, if applicable.
        # This is crucial for restoring the terminal to its normal state on exit.
        self._original_terminal_settings = None
        if os.name != 'nt':
            self._original_terminal_settings = termios.tcgetattr(sys.stdin)

        self._initialize_game()

    def _initialize_game(self):
        """
        Resets the game state to its initial configuration.
        Called at the start of a new game or upon restarting.
        """
        # Place snake near the left edge, centered vertically
        start_x = BOARD_WIDTH // 4
        start_y = BOARD_HEIGHT // 2
        # Snake is a list of (x, y) coordinates, head is at index 0
        self.snake = [(start_x - i, start_y) for i in range(INITIAL_SNAKE_LENGTH)]
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.speed = INITIAL_GAME_SPEED
        self._generate_food() # Place the first piece of food

    def _generate_food(self):
        """
        Generates a new random position for the food.
        Ensures the food does not spawn inside the snake's body.
        """
        while True:
            # Generate coordinates within the board boundaries, avoiding the outer wall
            x = random.randint(1, BOARD_WIDTH - 2)
            y = random.randint(1, BOARD_HEIGHT - 2)
            if (x, y) not in self.snake: # Food must not overlap with the snake
                self.food = (x, y)
                break

    def _get_input(self):
        """
        Reads a single character from the console without waiting for Enter
        and without echoing the character to the screen.
        Updates the snake's direction based on the input.
        Handles platform differences for non-blocking input.
        """
        key = None
        if os.name == 'nt':  # For Windows systems
            if msvcrt.kbhit(): # Check if a key has been pressed
                key = msvcrt.getch().decode('utf-8').lower() # Read the key
        else:  # For Unix-like systems (Linux, macOS)
            # Use select to check if stdin has data without blocking
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                key = sys.stdin.read(1).lower() # Read one character

        # Update direction based on input, preventing immediate reverse turns
        if key == 'w' and self.direction != DOWN:
            self.direction = UP
        elif key == 's' and self.direction != UP:
            self.direction = DOWN
        elif key == 'a' and self.direction != RIGHT:
            self.direction = LEFT
        elif key == 'd' and self.direction != LEFT:
            self.direction = RIGHT
        elif key == 'q': # 'q' to quit the game
            self.game_over = True
        elif key == 'r' and self.game_over: # 'r' to restart when game is over
            self._initialize_game()

    def _move_snake(self):
        """
        Calculates the snake's new position based on its current direction.
        Checks for collisions and handles food consumption.
        """
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # --- Collision Detection ---
        # 1. Wall collision: New head is outside board boundaries
        # 2. Self-collision: New head overlaps with any part of the snake's body
        if (new_head[0] < 0 or new_head[0] >= BOARD_WIDTH or
            new_head[1] < 0 or new_head[1] >= BOARD_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head) # Add new head to the front of the snake list

        # Check if the snake has eaten the food
        if new_head == self.food:
            self.score += 10 # Increase score
            # Increase speed, ensuring it doesn't get too fast
            self.speed = max(0.05, self.speed * 0.95)
            self._generate_food() # Generate new food
        else:
            self.snake.pop() # Remove tail segment if no food was eaten (snake doesn't grow)

    def _draw_game(self):
        """
        Clears the console screen and redraws the entire game board,
        including walls, snake, food, and score.
        """
        # Clear screen command for Windows ('cls') or Unix-like ('clear')
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create an empty 2D board representation
        board = [[EMPTY_CHAR for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        # Draw the outer walls
        for x in range(BOARD_WIDTH):
            board[0][x] = WALL_CHAR # Top wall
            board[BOARD_HEIGHT - 1][x] = WALL_CHAR # Bottom wall
        for y in range(BOARD_HEIGHT):
            board[y][0] = WALL_CHAR # Left wall
            board[y][BOARD_WIDTH - 1] = WALL_CHAR # Right wall

        # Draw the food
        if self.food:
            food_x, food_y = self.food
            # Ensure food coordinates are within bounds before drawing
            if 0 <= food_y < BOARD_HEIGHT and 0 <= food_x < BOARD_WIDTH:
                board[food_y][food_x] = FOOD_CHAR

        # Draw the snake
        for i, (x, y) in enumerate(self.snake):
            # Ensure snake segment coordinates are within bounds before drawing
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                if i == 0:
                    board[y][x] = HEAD_CHAR # Draw head
                else:
                    board[y][x] = BODY_CHAR # Draw body segment

        # Print the completed board row by row
        for row in board:
            print("".join(row))

        # Display score and game status messages
        print(f"Score: {self.score}")
        if self.game_over:
            print("\nGAME OVER! Press 'R' to restart or 'Q' to quit.")
        else:
            print("Use WASD to move. Press 'Q' to quit.")

    def _setup_terminal_input(self):
        """
        Configures the terminal for raw input mode on Unix-like systems.
        In raw mode, characters are read immediately without waiting for Enter,
        and are not echoed to the screen.
        """
        if os.name != 'nt':
            # Save current terminal settings to restore them later
            self._original_terminal_settings = termios.tcgetattr(sys.stdin)
            # Set terminal to raw mode
            tty.setraw(sys.stdin)

    def _restore_terminal_input(self):
        """
        Restores the terminal to its original settings on Unix-like systems.
        This is crucial to ensure the console behaves normally after the game exits.
        """
        if os.name != 'nt' and self._original_terminal_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_terminal_settings)

    def run(self):
        """
        Starts the main game loop.
        Handles game progression, input, drawing, and game over/restart logic.
        """
        try:
            self._setup_terminal_input() # Configure terminal for game input

            while True:
                self._get_input() # Process any available input

                if self.game_over:
                    self._draw_game() # Show "GAME OVER" screen
                    # Pause the game logic and wait for 'R' or 'Q' input
                    while self.game_over:
                        self._get_input() # Continuously check for restart/quit input
                        time.sleep(0.1) # Small delay to prevent busy-waiting
                        if not self.game_over: # Game was restarted by 'R'
                            break
                        # Explicitly check for 'q' to quit during game over state
                        # This avoids an extra frame rendering if 'q' is pressed immediately.
                        if (
                            ('q' == msvcrt.getch().decode('utf-8').lower() if os.name == 'nt' and msvcrt.kbhit() else False) or
                            ('q' == sys.stdin.read(1).lower() if os.name != 'nt' and select.select([sys.stdin], [], [], 0)[0] else False)
                        ):
                            self.game_over = True # Ensure game_over remains true to break outer loop
                            break
                    if self.game_over: # If game_over is still true (meaning 'q' was pressed)
                        break # Exit the main game loop

                self._move_snake() # Update snake position
                self._draw_game() # Redraw the game state
                time.sleep(self.speed) # Pause for game speed

        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C to exit the game
            pass
        finally:
            self._restore_terminal_input() # Always restore terminal settings on exit


if __name__ == "__main__":
    # Create an instance of the SnakeGame and run it.
    game = SnakeGame()
    game.run()
