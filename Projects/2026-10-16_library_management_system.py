"""
A beginner-friendly Library Management System script.

This script allows users to manage a collection of books.
It supports adding, listing, searching, borrowing, returning, and deleting books.
All library data is persisted to a JSON file named 'library_data.json'
so that it is saved between program runs.
"""

import json
import os
import sys # Used for sys.exit()

DATA_FILE = "library_data.json" # The file where library data will be stored.

class Library:
    """
    Manages the collection of books in the library.
    Handles operations like adding, listing, searching, borrowing,
    returning, and deleting books, as well as data persistence.
    """

    def __init__(self):
        """
        Initializes the Library. Loads existing book data from the DATA_FILE
        or starts with an empty library if the file doesn't exist.
        It also tracks the next available book ID to ensure uniqueness.
        """
        self.books = []
        self._next_book_id = 1
        self._load_data() # Load data when the Library object is created

    def _save_data(self):
        """
        Saves the current list of books to the DATA_FILE in JSON format.
        This method is called after any operation that modifies the book data.
        """
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.books, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """
        Loads book data from the DATA_FILE. If the file doesn't exist,
        it initializes an empty list of books. It also updates
        _next_book_id based on existing books to prevent ID conflicts.
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.books = json.load(f)
                # Find the maximum existing book ID and set _next_book_id
                # to one greater than that to ensure unique IDs for new books.
                if self.books:
                    self._next_book_id = max(book['id'] for book in self.books) + 1
                else:
                    self._next_book_id = 1
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading data from '{DATA_FILE}': {e}. Starting with an empty library.")
                self.books = []
                self._next_book_id = 1
        else:
            self.books = [] # If file doesn't exist, start fresh

    def _find_book_by_id(self, book_id):
        """
        Helper method to find a book in the library by its ID.
        Returns the book dictionary if found, otherwise None.
        """
        for book in self.books:
            if book['id'] == book_id:
                return book
        return None

    def add_book(self, title, author, isbn):
        """
        Adds a new book to the library with a unique ID.
        Each book is stored as a dictionary with its details.
        """
        # Check if a book with the same ISBN already exists to prevent duplicates
        for book in self.books:
            if book['isbn'] == isbn:
                print(f"Error: A book with ISBN '{isbn}' already exists (ID: {book['id']}).")
                return

        new_book = {
            'id': self._next_book_id,
            'title': title,
            'author': author,
            'isbn': isbn,
            'is_borrowed': False,
            'borrowed_by': None
        }
        self.books.append(new_book)
        self._next_book_id += 1 # Increment for the next new book
        self._save_data() # Save changes to the data file
        print(f"Book '{title}' added successfully with ID: {new_book['id']}.")

    def list_all_books(self):
        """
        Prints details of all books currently in the library.
        If no books are present, it prints a corresponding message.
        """
        if not self.books:
            print("The library is currently empty.")
            return

        print("\n--- All Books in Library ---")
        for book in self.books:
            status = "Borrowed" if book['is_borrowed'] else "Available"
            borrower_info = f" (by {book['borrowed_by']})" if book['borrowed_by'] else ""
            print(f"ID: {book['id']}, Title: {book['title']}, Author: {book['author']}, "
                  f"ISBN: {book['isbn']}, Status: {status}{borrower_info}")
        print("----------------------------")

    def search_book(self, query):
        """
        Searches for books whose title, author, or ISBN contains the query string (case-insensitive).
        Prints details of all matching books.
        """
        found_books = []
        query_lower = query.lower() # Convert query to lowercase for case-insensitive search

        for book in self.books:
            if (query_lower in book['title'].lower() or
                query_lower in book['author'].lower() or
                query_lower in book['isbn'].lower()):
                found_books.append(book)

        if not found_books:
            print(f"No books found matching '{query}'.")
            return

        print(f"\n--- Books matching '{query}' ---")
        for book in found_books:
            status = "Borrowed" if book['is_borrowed'] else "Available"
            borrower_info = f" (by {book['borrowed_by']})" if book['borrowed_by'] else ""
            print(f"ID: {book['id']}, Title: {book['title']}, Author: {book['author']}, "
                  f"ISBN: {book['isbn']}, Status: {status}{borrower_info}")
        print("----------------------------")

    def borrow_book(self, book_id, borrower_name):
        """
        Marks a book as borrowed.
        Requires the book ID and the name of the borrower.
        """
        book = self._find_book_by_id(book_id)
        if not book:
            print(f"Error: Book with ID {book_id} not found.")
            return

        if book['is_borrowed']:
            print(f"Error: Book '{book['title']}' (ID: {book_id}) is already borrowed by {book['borrowed_by']}.")
        else:
            book['is_borrowed'] = True
            book['borrowed_by'] = borrower_name
            self._save_data()
            print(f"Book '{book['title']}' (ID: {book_id}) has been successfully borrowed by {borrower_name}.")

    def return_book(self, book_id):
        """
        Marks a previously borrowed book as available.
        Requires the book ID.
        """
        book = self._find_book_by_id(book_id)
        if not book:
            print(f"Error: Book with ID {book_id} not found.")
            return

        if not book['is_borrowed']:
            print(f"Error: Book '{book['title']}' (ID: {book_id}) is not currently borrowed.")
        else:
            borrower_name = book['borrowed_by'] # Store borrower name before clearing
            book['is_borrowed'] = False
            book['borrowed_by'] = None
            self._save_data()
            print(f"Book '{book['title']}' (ID: {book_id}) previously borrowed by {borrower_name} "
                  f"has been successfully returned and is now available.")

    def delete_book(self, book_id):
        """
        Removes a book from the library by its ID.
        If the book is borrowed, it cannot be deleted.
        """
        book_to_delete = None
        for i, book in enumerate(self.books):
            if book['id'] == book_id:
                book_to_delete = book
                break

        if not book_to_delete:
            print(f"Error: Book with ID {book_id} not found.")
            return

        if book_to_delete['is_borrowed']:
            print(f"Error: Book '{book_to_delete['title']}' (ID: {book_id}) cannot be deleted "
                  f"because it is currently borrowed by {book_to_delete['borrowed_by']}.")
            return

        self.books.pop(i) # Remove the book from the list
        self._save_data() # Save changes to the data file
        print(f"Book '{book_to_delete['title']}' (ID: {book_id}) has been successfully deleted.")


def display_menu():
    """Prints the main menu options for the library system."""
    print("\n--- Library Management System ---")
    print("1. Add a new book")
    print("2. List all books")
    print("3. Search for a book")
    print("4. Borrow a book")
    print("5. Return a book")
    print("6. Delete a book")
    print("7. Exit")
    print("---------------------------------")

def get_valid_input(prompt, type_func=str, error_msg="Invalid input. Please try again."):
    """
    Helper function to get validated input from the user.
    Repeats the prompt until valid input is provided.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input: # Ensure input is not empty for string types
                raise ValueError("Input cannot be empty.")
            return type_func(user_input)
        except ValueError:
            print(error_msg)

if __name__ == "__main__":
    library = Library() # Create an instance of the Library

    while True:
        display_menu()
        choice = get_valid_input("Enter your choice (1-7): ", int, "Invalid choice. Please enter a number between 1 and 7.")

        if choice == 1:
            # Add a new book
            title = get_valid_input("Enter book title: ")
            author = get_valid_input("Enter book author: ")
            isbn = get_valid_input("Enter book ISBN: ")
            library.add_book(title, author, isbn)
        elif choice == 2:
            # List all books
            library.list_all_books()
        elif choice == 3:
            # Search for a book
            query = get_valid_input("Enter search query (title, author, or ISBN): ")
            library.search_book(query)
        elif choice == 4:
            # Borrow a book
            book_id = get_valid_input("Enter the ID of the book to borrow: ", int, "Invalid ID. Please enter a number.")
            borrower_name = get_valid_input("Enter borrower's name: ")
            library.borrow_book(book_id, borrower_name)
        elif choice == 5:
            # Return a book
            book_id = get_valid_input("Enter the ID of the book to return: ", int, "Invalid ID. Please enter a number.")
            library.return_book(book_id)
        elif choice == 6:
            # Delete a book
            book_id = get_valid_input("Enter the ID of the book to delete: ", int, "Invalid ID. Please enter a number.")
            library.delete_book(book_id)
        elif choice == 7:
            # Exit the program
            print("Exiting Library Management System. Goodbye!")
            sys.exit(0) # Use sys.exit() for a clean exit
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

        input("\nPress Enter to continue...") # Pause for user to read output
