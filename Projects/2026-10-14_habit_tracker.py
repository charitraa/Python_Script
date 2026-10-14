"""
A simple command-line habit tracker.

This script allows users to add new habits, mark habits as complete for the current day,
view a list of all habits with their progress (total completions, last completion, and current streak),
and delete habits. All habit data is stored in a JSON file named 'habits_data.json'
in the same directory as the script.

Features:
- Add a new habit.
- Mark a habit as completed for today.
- View all habits with summary statistics.
- Delete an existing habit.
- Data persistence using a JSON file.
"""

import json
import datetime
import os

HABITS_FILE = "habits_data.json" # The file where habit data will be stored.
DATE_FORMAT = "%Y-%m-%d" # Standard date format for storing and displaying dates.

def get_today_date():
    """Returns today's date as a string in YYYY-MM-DD format."""
    return datetime.date.today().strftime(DATE_FORMAT)

def load_habits():
    """
    Loads habits from the JSON file.
    If the file does not exist, an empty dictionary is returned.
    If the file is empty or corrupted, a warning is printed, and an empty dictionary is returned.
    """
    if not os.path.exists(HABITS_FILE):
        return {}
    try:
        with open(HABITS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Handle cases where the JSON file is empty or contains malformed JSON
        print(f"Warning: {HABITS_FILE} is corrupted or empty. Starting with no habits.")
        return {}
    except Exception as e:
        # Catch any other potential file reading errors
        print(f"An unexpected error occurred while loading habits: {e}")
        return {}

def save_habits(habits):
    """Saves the current habits dictionary to the JSON file."""
    try:
        with open(HABITS_FILE, 'w') as f:
            json.dump(habits, f, indent=4) # Use indent for pretty printing the JSON
    except Exception as e:
        print(f"Error saving habits: {e}")

def add_habit(habits, name):
    """
    Adds a new habit to the tracker.
    Initializes the habit with the current date and an empty list of completion dates.
    Performs a case-insensitive check to prevent adding duplicate habit names.
    """
    # Check if a habit with the same name (case-insensitive) already exists
    if name.lower() in [h.lower() for h in habits]:
        print(f"Habit '{name}' already exists.")
        return

    today = get_today_date()
    habits[name] = {
        "created_date": today,
        "completion_dates": []
    }
    print(f"Habit '{name}' added successfully!")
    save_habits(habits)

def mark_habit_complete(habits, name):
    """
    Marks a habit as complete for the current day.
    Prevents duplicate entries if the habit is already marked complete for today.
    Ensures completion dates are sorted.
    """
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return

    today = get_today_date()
    if today in habits[name]["completion_dates"]:
        print(f"Habit '{name}' already marked complete for today ({today}).")
        return

    habits[name]["completion_dates"].append(today)
    habits[name]["completion_dates"].sort() # Keep dates sorted for easier streak calculation
    print(f"Habit '{name}' marked complete for today ({today})!")
    save_habits(habits)

def calculate_current_streak(completion_dates):
    """
    Calculates the current consecutive daily streak for a habit.
    A streak counts consecutive completions *up to and including today*.
    If today is not completed, the current streak is considered 0.
    """
    if not completion_dates:
        return 0

    # Convert date strings to datetime.date objects for easier comparison
    dates = sorted([datetime.datetime.strptime(d, DATE_FORMAT).date() for d in completion_dates])
    
    current_streak = 0
    today = datetime.date.today()

    # If today's date is not in the completion dates, the current streak is 0.
    if today not in dates:
        return 0 
    
    # If today is complete, start counting the streak from today
    current_streak = 1
    # Check the day before today, and keep going backwards
    check_date = today - datetime.timedelta(days=1)
    
    # Iterate backwards through days, checking if each day was completed
    while check_date in dates:
        current_streak += 1
        check_date -= datetime.timedelta(days=1)
    
    return current_streak

def view_habits(habits):
    """
    Displays a list of all habits, their creation date,
    total completions, last completion date, and current streak.
    """
    if not habits:
        print("\nNo habits tracked yet. Add a new habit to get started!")
        return

    print("\n--- Your Habits ---")
    # Sort habits alphabetically by name for consistent display
    for name in sorted(habits.keys()):
        data = habits[name]
        creation_date = data["created_date"]
        completions = data["completion_dates"]
        total_completions = len(completions)
        last_completion = completions[-1] if completions else "Never"
        current_streak = calculate_current_streak(completions)

        print(f"\nHabit: {name}")
        print(f"  Created: {creation_date}")
        print(f"  Total Completions: {total_completions}")
        print(f"  Last Completed: {last_completion}")
        print(f"  Current Streak: {current_streak} day(s)")
    print("-------------------\n")

def delete_habit(habits, name):
    """Deletes a habit from the tracker."""
    if name not in habits:
        print(f"Habit '{name}' not found.")
        return

    del habits[name]
    print(f"Habit '{name}' deleted successfully!")
    save_habits(habits)

def display_menu():
    """Displays the main menu options to the user."""
    print("\n--- Habit Tracker Menu ---")
    print("1. Add a new habit")
    print("2. Mark habit complete for today")
    print("3. View all habits")
    print("4. Delete a habit")
    print("5. Exit")
    print("--------------------------")

def main():
    """Main function to run the habit tracker application."""
    habits = load_habits() # Load habits from the file at startup

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip() # Get user input and remove whitespace

        if choice == '1':
            habit_name = input("Enter the name of the new habit: ").strip()
            if habit_name: # Ensure habit name is not empty
                add_habit(habits, habit_name)
            else:
                print("Habit name cannot be empty.")
        elif choice == '2':
            habit_name = input("Enter the name of the habit to mark complete: ").strip()
            if habit_name:
                mark_habit_complete(habits, habit_name)
            else:
                print("Habit name cannot be empty.")
        elif choice == '3':
            view_habits(habits)
        elif choice == '4':
            habit_name = input("Enter the name of the habit to delete: ").strip()
            if habit_name:
                delete_habit(habits, habit_name)
            else:
                print("Habit name cannot be empty.")
        elif choice == '5':
            print("Exiting Habit Tracker. Goodbye!")
            break # Exit the loop and end the program
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
