"""
A simple command-line expense tracker that allows users to add, view, and summarize
their expenses. Expenses are stored in a JSON file for persistence, making them
available across different sessions.
"""

import json
import os
from datetime import datetime

# Define the filename where expenses will be stored.
# This file will be created in the same directory as the script.
EXPENSE_FILE = "expenses.json"

def load_expenses():
    """
    Loads expenses from the EXPENSE_FILE.
    
    If the file does not exist, is empty, or contains invalid JSON, an empty list
    is returned, and a warning is printed. This ensures the application can
    start fresh or recover from corrupted data without crashing.

    Returns:
        list: A list of dictionaries, where each dictionary represents an expense.
              Returns an empty list if no expenses are found or an error occurs.
    """
    # Check if the expense file exists.
    if not os.path.exists(EXPENSE_FILE):
        return [] # Return an empty list if the file doesn't exist yet.

    try:
        with open(EXPENSE_FILE, 'r', encoding='utf-8') as f:
            expenses = json.load(f)
            # Validate that the loaded data is a list and contains valid expense dictionaries.
            if not isinstance(expenses, list) or not all(
                isinstance(e, dict) and 'date' in e and 'description' in e and 'amount' in e
                for e in expenses
            ):
                print("Warning: Expense file content is invalid. Starting with empty expenses.")
                return []
            return expenses
    except json.JSONDecodeError:
        # Handles cases where the file exists but is not valid JSON (e.g., empty, malformed).
        print(f"Warning: Expense file '{EXPENSE_FILE}' is corrupted. Starting with empty expenses.")
        return []
    except Exception as e:
        # Catch any other unexpected errors during file loading.
        print(f"An unexpected error occurred while loading expenses: {e}. Starting with empty expenses.")
        return []

def save_expenses(expenses):
    """
    Saves the current list of expenses to the EXPENSE_FILE in JSON format.
    
    Args:
        expenses (list): The list of expense dictionaries to be saved.
    """
    try:
        with open(EXPENSE_FILE, 'w', encoding='utf-8') as f:
            # json.dump serializes the Python list to a JSON formatted string.
            # indent=4 makes the JSON file human-readable with 4-space indentation.
            json.dump(expenses, f, indent=4)
    except Exception as e:
        # Catch any errors that might occur during the saving process.
        print(f"Error saving expenses: {e}")

def add_expense(expenses):
    """
    Prompts the user for expense details (date, description, amount)
    and adds a new expense dictionary to the expenses list.
    Includes input validation for date and amount.
    
    Args:
        expenses (list): The list to which the new expense will be added.
    """
    print("\n--- Add New Expense ---")
    
    # Loop until a valid date is entered.
    while True:
        date_str = input("Enter date (YYYY-MM-DD): ")
        try:
            # Attempt to parse the date string to validate its format.
            datetime.strptime(date_str, "%Y-%m-%d")
            break # Exit loop if date is valid.
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    description = input("Enter description: ")
    
    # Loop until a valid positive amount is entered.
    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be a positive number.")
            else:
                break # Exit loop if amount is valid.
        except ValueError:
            print("Invalid amount. Please enter a number.")
            
    # Create a dictionary for the new expense.
    expense = {
        "date": date_str,
        "description": description,
        "amount": amount
    }
    expenses.append(expense)
    print("Expense added successfully!")

def view_expenses(expenses):
    """
    Displays all recorded expenses in a formatted table.
    Expenses are sorted by date for better readability.
    
    Args:
        expenses (list): The list of expense dictionaries to display.
    """
    if not expenses:
        print("\nNo expenses recorded yet.")
        return
    
    print("\n--- Your Expenses ---")
    # Define header for the table.
    # f-string formatting is used for alignment: < for left, > for right.
    print(f"{'Date':<12} {'Description':<30} {'Amount':>10}")
    print("-" * 54) # Separator line for readability.
    
    # Sort expenses by date. The lambda function specifies 'date' as the key for sorting.
    sorted_expenses = sorted(expenses, key=lambda x: x['date'])

    for expense in sorted_expenses:
        # Print each expense, formatting amount to two decimal places.
        print(f"{expense['date']:<12} {expense['description']:<30} {expense['amount']:>10.2f}")

    print("-" * 54) # Bottom separator line.

def get_total_expenses(expenses):
    """
    Calculates and prints the total sum of all recorded expenses.
    
    Args:
        expenses (list): The list of expense dictionaries.

    Returns:
        float: The total sum of all expenses.
    """
    # Sums the 'amount' of each expense in the list.
    total = sum(expense['amount'] for expense in expenses)
    print(f"\nTotal expenses: ${total:.2f}")
    return total

def display_menu():
    """
    Prints the main menu options to the console, guiding the user.
    """
    print("\n--- Expense Tracker Menu ---")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Get Total Expenses")
    print("4. Exit")
    print("--------------------------")

def run_tracker():
    """
    Main function to run the expense tracker application loop.
    It loads expenses at startup, displays a menu, and performs actions
    based on user input until the user chooses to exit.
    """
    # Load existing expenses from the file when the tracker starts.
    expenses = load_expenses()
    
    while True:
        display_menu() # Show the user the available options.
        choice = input("Enter your choice: ")
        
        if choice == '1':
            add_expense(expenses)
            save_expenses(expenses) # Save expenses immediately after adding a new one.
        elif choice == '2':
            view_expenses(expenses)
        elif choice == '3':
            get_total_expenses(expenses)
        elif choice == '4':
            print("Exiting Expense Tracker. Goodbye!")
            break # Exit the infinite loop, thus ending the program.
        else:
            print("Invalid choice. Please try again.")

# This block ensures that `run_tracker()` is called only when the script is
# executed directly (e.g., `python expense_tracker.py`), not when it's
# imported as a module into another Python script.
if __name__ == "__main__":
    run_tracker() # Start the expense tracker application.
