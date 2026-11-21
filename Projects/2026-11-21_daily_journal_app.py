"""
A simple command-line daily journal application.

This script allows users to add new journal entries, view all existing entries,
or view entries from a specific date. Entries are stored persistently in a
SQLite database file named 'journal.db' in the same directory as the script.

Features:
- Add a new journal entry with the current date.
- View all journal entries sorted by date.
- View journal entries for a specific date.
- All data is stored locally in an SQLite database.
- Designed to be beginner-friendly with clear prompts and output.
"""

import sqlite3
import datetime
import os

DATABASE_NAME = 'journal.db' # The name of the SQLite database file.

def _get_db_connection():
    """Establishes a connection to the SQLite database and returns the connection object.
    The row_factory is set to sqlite3.Row to allow accessing columns by name."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def _initialize_database():
    """
    Initializes the database by creating the 'entries' table if it doesn't already exist.
    The table has columns for id (primary key), date (text), and content (text).
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def _clear_screen():
    """Clears the terminal screen for better readability during interactions."""
    # 'nt' is for Windows, 'posix' is for Linux/macOS
    os.system('cls' if os.name == 'nt' else 'clear')

def add_entry():
    """
    Prompts the user to enter a journal entry and saves it to the database
    with the current date (YYYY-MM-DD format). Handles empty entry input.
    """
    _clear_screen()
    print("--- Add New Journal Entry ---")
    entry_content = input("Enter your journal entry (press Enter when done): ")
    
    # Check if the entry content is empty or just whitespace
    if not entry_content.strip():
        print("Entry cannot be empty. Returning to main menu.")
        input("Press Enter to continue...")
        return

    current_date = datetime.date.today().isoformat() # Gets today's date in YYYY-MM-DD format

    conn = _get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert the current date and user's entry content into the database
        cursor.execute("INSERT INTO entries (date, content) VALUES (?, ?)", (current_date, entry_content))
        conn.commit()
        print("\nEntry added successfully!")
    except sqlite3.Error as e:
        # Catch any potential database errors during insertion
        print(f"An error occurred while adding the entry: {e}")
    finally:
        conn.close() # Always close the connection
    input("Press Enter to continue...")

def view_entries(date_filter=None):
    """
    Retrieves and displays journal entries from the database.
    If a `date_filter` (string in YYYY-MM-DD format) is provided, it shows entries
    for that specific date. Otherwise, it shows all entries, ordered by date and then ID.
    """
    _clear_screen()
    conn = _get_db_connection()
    cursor = conn.cursor()
    entries = []

    try:
        if date_filter:
            print(f"--- Journal Entries for {date_filter} ---")
            # Select entries matching the specific date filter
            cursor.execute("SELECT id, date, content FROM entries WHERE date = ? ORDER BY id ASC", (date_filter,))
        else:
            print("--- All Journal Entries ---")
            # Select all entries, ordered by date and then ID for consistent display
            cursor.execute("SELECT id, date, content FROM entries ORDER BY date ASC, id ASC")
        
        entries = cursor.fetchall() # Fetch all results from the query

        if not entries:
            print("No entries found.")
        else:
            for entry in entries:
                # Access columns by name because `row_factory = sqlite3.Row` was set
                print(f"\n[{entry['date']}] (ID: {entry['id']})")
                print(f"  {entry['content']}")
                print("-" * 30) # A visual separator for each entry
    except sqlite3.Error as e:
        # Catch any potential database errors during retrieval
        print(f"An error occurred while viewing entries: {e}")
    finally:
        conn.close() # Always close the connection
    input("Press Enter to continue...")


def main_menu():
    """
    Displays the main menu of the journal app and handles user choices.
    It loops until the user chooses to exit.
    """
    while True:
        _clear_screen()
        print("--- Daily Journal App ---")
        print("1. Add New Entry")
        print("2. View All Entries")
        print("3. View Entries by Date")
        print("4. Exit")
        print("-------------------------")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            add_entry()
        elif choice == '2':
            view_entries()
        elif choice == '3':
            _clear_screen()
            print("--- View Entries by Date ---")
            date_input = input("Enter date (YYYY-MM-DD): ")
            try:
                # Validate date format by attempting to convert it to a date object
                datetime.date.fromisoformat(date_input)
                view_entries(date_input)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                input("Press Enter to continue...")
        elif choice == '4':
            print("Exiting Journal App. Goodbye!")
            break # Exit the main loop
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    # This block ensures that _initialize_database() is called and main_menu()
    # is executed only when the script is run directly.
    _initialize_database() # Ensure the database and table exist before starting the app
    main_menu()
