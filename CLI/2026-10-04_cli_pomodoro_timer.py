"""
A simple command-line Pomodoro Timer.

This script implements a basic Pomodoro technique timer directly in the terminal.
It cycles through work sessions and short breaks, with a long break after
every four work sessions. The user can start, pause, and exit the timer.

Features:
- Configurable work session duration.
- Configurable short break duration.
- Configurable long break duration.
- Visual countdown in the terminal that overwrites itself.
- Clears the terminal for a cleaner display.
- Basic prompts for user interaction (start/quit).
- Uses only standard Python library modules.
"""

import time
import os
import sys

# --- Configuration ---
# All durations are in minutes.
WORK_DURATION_MINUTES = 25
SHORT_BREAK_DURATION_MINUTES = 5
LONG_BREAK_DURATION_MINUTES = 15
SESSIONS_BEFORE_LONG_BREAK = 4 # Number of work sessions before a long break

# --- Helper Functions ---

def clear_screen():
    """Clears the terminal screen."""
    # 'cls' is for Windows, 'clear' is for macOS/Linux/Unix-like systems.
    os.system('cls' if os.name == 'nt' else 'clear')

def countdown_timer(duration_seconds, session_type):
    """
    Counts down the given duration, updating the terminal display on a single line.

    Args:
        duration_seconds (int): The total duration for the countdown in seconds.
        session_type (str): A string indicating the type of session (e.g., "Work", "Short Break").
    """
    start_time = time.time()
    end_time = start_time + duration_seconds

    while time.time() < end_time:
        remaining_seconds = int(end_time - time.time())
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        # Display the timer.
        # '\r' moves the cursor to the beginning of the line without clearing it,
        # allowing us to overwrite the previous output.
        # `sys.stdout.write` is used for more granular control over output than `print()`.
        # `flush=True` ensures the output is immediately written to the console,
        # which is crucial for the real-time update effect.
        sys.stdout.write(f"\r{session_type}: {minutes:02d}:{seconds:02d} remaining...")
        sys.stdout.flush()

        time.sleep(1) # Wait for 1 second before updating the display again.

    # After the countdown, print a final message and a newline character.
    # The `\n` ensures that subsequent print statements start on a new line.
    sys.stdout.write(f"\r{session_type}: 00:00 -- Time's up!              \n")
    sys.stdout.flush()

def play_sound_notification(message):
    """
    A simple "sound" notification for the CLI.
    Prints a prominent message to indicate session changes.
    """
    print(f"\n{'='*30}")
    print(f"!!! {message} !!!")
    print(f"{'='*30}\n")
    # For a simple beep (often not reliably audible or cross-platform without external libs):
    # print('\a', end='') # ASCII bell character - might make a sound or not.

# --- Main Logic ---

def run_pomodoro_timer():
    """
    Runs the main Pomodoro timer loop.
    Manages work sessions, short breaks, and long breaks based on configuration.
    """
    work_sessions_completed = 0
    print("Welcome to the CLI Pomodoro Timer!")
    print(f"Work: {WORK_DURATION_MINUTES} min | Short Break: {SHORT_BREAK_DURATION_MINUTES} min | Long Break: {LONG_BREAK_DURATION_MINUTES} min")
    print(f"Long break after {SESSIONS_BEFORE_LONG_BREAK} work sessions.")

    while True:
        # Prompt user to start a work session or quit the timer.
        action = input("Press 's' to start a work session, or 'q' to quit: ").lower()
        if action == 'q':
            print("Exiting Pomodoro Timer. Goodbye!")
            break # Exit the main loop, ending the program.
        elif action != 's':
            print("Invalid input. Please enter 's' or 'q'.")
            continue # Go back to the beginning of the loop to ask again.

        clear_screen()
        play_sound_notification("STARTING WORK SESSION")
        countdown_timer(WORK_DURATION_MINUTES * 60, "Work")
        play_sound_notification("WORK SESSION ENDED")

        work_sessions_completed += 1
        print(f"Work sessions completed: {work_sessions_completed}")

        if work_sessions_completed % SESSIONS_BEFORE_LONG_BREAK == 0:
            # It's time for a long break after completing the configured number of work sessions.
            print("\nIt's time for a long break!")
            action = input("Press 's' to start your long break, or 'q' to quit: ").lower()
            if action == 'q':
                print("Exiting Pomodoro Timer. Goodbye!")
                break
            elif action != 's':
                print("Invalid input. Starting long break anyway.") # Simplified: force break if not 'q'
            
            clear_screen()
            play_sound_notification("STARTING LONG BREAK")
            countdown_timer(LONG_BREAK_DURATION_MINUTES * 60, "Long Break")
            play_sound_notification("LONG BREAK ENDED")
        else:
            # It's time for a short break.
            print("\nIt's time for a short break!")
            action = input("Press 's' to start your short break, or 'q' to quit: ").lower()
            if action == 'q':
                print("Exiting Pomodoro Timer. Goodbye!")
                break
            elif action != 's':
                print("Invalid input. Starting short break anyway.") # Simplified: force break if not 'q'

            clear_screen()
            play_sound_notification("STARTING SHORT BREAK")
            countdown_timer(SHORT_BREAK_DURATION_MINUTES * 60, "Short Break")
            play_sound_notification("SHORT BREAK ENDED")

        # The loop will naturally return to the top, prompting the user for the next session.

# --- Main Execution Block ---

if __name__ == "__main__":
    # This block ensures that `run_pomodoro_timer()` is called only when
    # the script is executed directly (not when imported as a module).
    run_pomodoro_timer()
