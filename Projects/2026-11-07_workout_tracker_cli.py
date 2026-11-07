"""
A simple command-line interface (CLI) workout tracker.

This script allows users to add, view, and delete workout sessions.
Workout data is stored in a JSON file named 'workouts.json' for persistence.

Features:
- Add new workout entries with date, type, duration, and notes.
- View all recorded workout sessions.
- Delete existing workout sessions by their index.
- Data is automatically loaded on startup and saved on exit or after modifications.
"""

import json
import os
from datetime import datetime

# --- Constants ---
DATA_FILE = "workouts.json" # The file where workout data will be stored.

# --- Global Data (loaded/saved) ---
workouts = [] # This list will hold all workout dictionaries.

# --- Helper Functions ---

def load_workouts():
    """Loads workout data from the DATA_FILE."""
    global workouts
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                workouts = json.load(f)
            print(f"Loaded {len(workouts)} workouts from {DATA_FILE}")
        except json.JSONDecodeError:
            # Handle cases where the JSON file might be empty or corrupted
            print(f"Warning: {DATA_FILE} is empty or corrupted. Starting with an empty workout list.")
            workouts = []
        except Exception as e:
            print(f"An unexpected error occurred while loading workouts: {e}")
            workouts = []
    else:
        print(f"No {DATA_FILE} found. Starting with an empty workout list.")
        workouts = []

def save_workouts():
    """Saves the current workout data to the DATA_FILE."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(workouts, f, indent=4) # Use indent for pretty printing JSON
        print(f"Workouts saved to {DATA_FILE}")
    except Exception as e:
        print(f"Error saving workouts: {e}")

def display_workout(index, workout):
    """Prints a single workout's details in a user-friendly format."""
    print(f"--- Workout {index + 1} ---")
    print(f"Date: {workout.get('date', 'N/A')}")
    print(f"Type: {workout.get('type', 'N/A')}")
    print(f"Duration: {workout.get('duration_minutes', 'N/A')} minutes")
    print(f"Notes: {workout.get('notes', 'N/A')}")
    print("-" * 20)

# --- Main CLI Functions ---

def add_workout():
    """Prompts the user for workout details and adds a new workout entry."""
    print("\n--- Add New Workout ---")
    
    # Get current date in YYYY-MM-DD format
    workout_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Date (auto-filled): {workout_date}")

    workout_type = input("Enter workout type (e.g., Strength, Cardio, Yoga): ").strip()
    if not workout_type:
        print("Workout type cannot be empty. Aborting add operation.")
        return

    duration_minutes = 0
    while True:
        try:
            duration_str = input("Enter duration in minutes: ").strip()
            duration_minutes = int(duration_str)
            if duration_minutes <= 0:
                print("Duration must be a positive number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number for duration.")
    
    notes = input("Enter any notes (optional): ").strip()

    new_workout = {
        "date": workout_date,
        "type": workout_type,
        "duration_minutes": duration_minutes,
        "notes": notes
    }
    
    workouts.append(new_workout)
    save_workouts()
    print("Workout added successfully!")

def view_workouts():
    """Displays all recorded workout sessions."""
    print("\n--- Your Workouts ---")
    if not workouts:
        print("No workouts recorded yet. Add some to see them here!")
        return

    for i, workout in enumerate(workouts):
        display_workout(i, workout)

def delete_workout():
    """Allows the user to delete a workout by its index."""
    print("\n--- Delete Workout ---")
    if not workouts:
        print("No workouts to delete.")
        return

    view_workouts() # Show workouts to help user choose which to delete

    while True:
        try:
            index_str = input("Enter the workout number to delete (e.g., 1 for the first workout): ").strip()
            workout_num_to_delete = int(index_str)
            
            # Convert user-friendly 1-based index to 0-based list index
            actual_index = workout_num_to_delete - 1 

            if 0 <= actual_index < len(workouts):
                deleted_workout = workouts.pop(actual_index)
                save_workouts()
                print(f"Workout on {deleted_workout.get('date')} of type '{deleted_workout.get('type')}' deleted successfully.")
                break
            else:
                print("Invalid workout number. Please enter a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def main_menu():
    """Displays the main menu and handles user choices."""
    load_workouts() # Load workouts at the start of the application

    while True:
        print("\n--- Workout Tracker Menu ---")
        print("1. Add New Workout")
        print("2. View All Workouts")
        print("3. Delete Workout")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            add_workout()
        elif choice == '2':
            view_workouts()
        elif choice == '3':
            delete_workout()
        elif choice == '4':
            print("Exiting Workout Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

# --- Main execution block ---
if __name__ == "__main__":
    main_menu()
