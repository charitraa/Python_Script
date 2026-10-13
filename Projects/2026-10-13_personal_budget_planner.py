"""
A simple command-line Personal Budget Planner.

This script allows users to:
1.  Add income transactions.
2.  Add expense transactions.
3.  View all recorded transactions.
4.  View a summary of their total income, total expenses, and remaining balance.

All transactions are saved to a plain text file (`transactions.txt`) for persistence,
meaning data is preserved even after the program closes.
The script is designed to be beginner-friendly, using basic file I/O and
fundamental Python data structures (lists and dictionaries).
"""

import os
from datetime import datetime

# --- Constants ---
TRANSACTIONS_FILE = "transactions.txt"  # The file where transaction data will be stored

# --- Helper Functions for File I/O ---

def load_transactions():
    """
    Loads transactions from the TRANSACTIONS_FILE.
    Each line in the file should be formatted as: type,description,amount,timestamp
    
    Returns:
        list: A list of dictionaries, where each dictionary represents a transaction.
              Returns an empty list if the file doesn't exist or is empty.
    """
    transactions = []
    # Check if the transactions file exists. If not, there are no transactions to load.
    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions

    try:
        # Open the file in read mode ('r')
        with open(TRANSACTIONS_FILE, 'r') as f:
            for line in f:
                # Remove leading/trailing whitespace and split the line by commas
                parts = line.strip().split(',')
                # Ensure the line has all four expected parts (type, description, amount, timestamp)
                if len(parts) == 4:
                    try:
                        # Convert the amount part to a float, handling potential errors
                        amount = float(parts[2])
                        transactions.append({
                            "type": parts[0],
                            "description": parts[1],
                            "amount": amount,
                            "timestamp": parts[3]
                        })
                    except ValueError:
                        # If the amount cannot be converted to a float, skip this line
                        print(f"Skipping malformed transaction amount in line: {line.strip()}")
                else:
                    # If the line does not have 4 parts, it's malformed
                    print(f"Skipping malformed transaction line: {line.strip()}")
    except IOError as e:
        # Catch any errors that occur during file reading
        print(f"Error loading transactions from {TRANSACTIONS_FILE}: {e}")
    return transactions

def save_transactions(transactions):
    """
    Saves the current list of transactions to TRANSACTIONS_FILE.
    Each transaction dictionary is converted into a comma-separated string on a new line.

    Args:
        transactions (list): The list of transaction dictionaries to save.
    """
    try:
        # Open the file in write mode ('w'). This will create the file if it doesn't exist,
        # or overwrite its contents if it does.
        with open(TRANSACTIONS_FILE, 'w') as f:
            for t in transactions:
                # Format each transaction dictionary into a comma-separated string.
                # Use {:.2f} to ensure amounts are saved with two decimal places.
                f.write(f"{t['type']},{t['description']},{t['amount']:.2f},{t['timestamp']}\n")
    except IOError as e:
        # Catch any errors that occur during file writing
        print(f"Error saving transactions to {TRANSACTIONS_FILE}: {e}")

# --- Core Budget Planner Functions ---

def add_transaction(transactions, transaction_type):
    """
    Prompts the user for details and adds a new transaction (income or expense)
    to the list of transactions. The updated list is then saved to the file.

    Args:
        transactions (list): The current list of transaction dictionaries.
        transaction_type (str): The type of transaction to add, either 'income' or 'expense'.
    """
    while True:
        description = input(f"Enter description for {transaction_type}: ").strip()
        if description:  # Ensure description is not empty
            break
        else:
            print("Description cannot be empty. Please try again.")

    while True:
        try:
            amount = float(input(f"Enter amount for {transaction_type}: "))
            if amount <= 0:  # Ensure amount is a positive number
                print("Amount must be a positive number. Please try again.")
            else:
                break
        except ValueError:
            # Catch error if user input is not a valid number
            print("Invalid amount. Please enter a numerical value.")

    # Get the current timestamp for the transaction
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a new transaction dictionary and add it to the list
    transactions.append({
        "type": transaction_type,
        "description": description,
        "amount": amount,
        "timestamp": timestamp
    })
    # Save transactions immediately after adding a new one to ensure persistence
    save_transactions(transactions)
    print(f"{transaction_type.capitalize()} added successfully!")

def view_transactions(transactions):
    """
    Displays all recorded transactions in a readable, tabular format.

    Args:
        transactions (list): The list of transaction dictionaries to display.
    """
    if not transactions:
        print("\nNo transactions recorded yet.")
        return

    print("\n--- All Transactions ---")
    # Print table headers
    print(f"{'Type':<10} {'Description':<30} {'Amount':>10} {'Date':>20}")
    print("-" * 72)  # Separator line

    for t in transactions:
        # Format amount to two decimal places for currency display
        amount_str = f"{t['amount']:.2f}"
        # Print each transaction in a formatted row
        print(f"{t['type'].capitalize():<10} {t['description']:<30} {amount_str:>10} {t['timestamp']:>20}")
    print("-" * 72)  # Separator line

def view_summary(transactions):
    """
    Calculates and displays the total income, total expenses, and the remaining balance.

    Args:
        transactions (list): The list of transaction dictionaries to summarize.
    """
    total_income = 0.0
    total_expenses = 0.0

    # Iterate through transactions to sum up income and expenses
    for t in transactions:
        if t['type'] == 'income':
            total_income += t['amount']
        elif t['type'] == 'expense':
            total_expenses += t['amount']

    remaining_balance = total_income - total_expenses

    print("\n--- Budget Summary ---")
    # Format currency amounts with commas for readability (e.g., $1,000.00)
    print(f"Total Income:    ${total_income:,.2f}")
    print(f"Total Expenses:  ${total_expenses:,.2f}")
    print(f"----------------------")
    print(f"Remaining Balance: ${remaining_balance:,.2f}")
    print("----------------------")

# --- User Interface Functions ---

def display_menu():
    """
    Prints the main menu options to the console for user interaction.
    """
    print("\n--- Personal Budget Planner ---")
    print("1. Add Income")
    print("2. Add Expense")
    print("3. View All Transactions")
    print("4. View Budget Summary")
    print("5. Exit")
    print("-------------------------------")

def main():
    """
    Main function to run the Personal Budget Planner application.
    It loads existing transactions, displays a menu, and handles user choices
    in a loop until the user decides to exit.
    """
    transactions = load_transactions()  # Load existing transactions when the program starts

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip() # Get user input and remove whitespace

        if choice == '1':
            add_transaction(transactions, 'income')
        elif choice == '2':
            add_transaction(transactions, 'expense')
        elif choice == '3':
            view_transactions(transactions)
        elif choice == '4':
            view_summary(transactions)
        elif choice == '5':
            print("Exiting Budget Planner. Goodbye!")
            break  # Exit the infinite loop, terminating the program
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# --- Script Entry Point ---

# This block ensures that `main()` is called only when the script is executed directly,
# not when it's imported as a module into another script.
if __name__ == "__main__":
    main()
