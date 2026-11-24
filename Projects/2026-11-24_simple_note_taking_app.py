"""
Simple Note-Taking App

This script provides a command-line interface for managing simple text notes.
It allows users to add, view, edit, and delete notes.
Notes are stored in a plain text file, with each note occupying a single line.
It's designed to be beginner-friendly and uses only standard Python libraries.
"""

import os # Used for checking if the notes file exists

NOTES_FILE = "notes.txt" # The file where notes will be stored

def load_notes(filename):
    """
    Loads notes from the specified file.
    Each line in the file is considered a separate note.
    Returns a list of notes.
    """
    notes = []
    # Check if the notes file exists. If not, return an empty list.
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Remove leading/trailing whitespace, including newline characters, from each line
                notes.append(line.strip()) 
    return notes

def save_notes(filename, notes):
    """
    Saves the list of notes to the specified file.
    Each note is written on a new line.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for note in notes:
            # Write each note followed by a newline character
            f.write(note + '\n') 

def display_menu():
    """
    Displays the main menu options to the user.
    """
    print("\n--- Simple Note-Taking App ---")
    print("1. View Notes")
    print("2. Add Note")
    print("3. Edit Note")
    print("4. Delete Note")
    print("5. Exit")
    print("------------------------------")

def view_notes(notes):
    """
    Displays all current notes with their corresponding indices.
    If there are no notes, it informs the user.
    """
    if not notes:
        print("\nNo notes available.")
        return

    print("\n--- Your Notes ---")
    # Enumerate to get both index and note for display
    for i, note in enumerate(notes):
        # Display 1-based index for user-friendliness (list is 0-based)
        print(f"{i + 1}. {note}") 
    print("------------------")

def add_note(notes):
    """
    Prompts the user to enter a new note and adds it to the list.
    Ensures the note content is not empty.
    """
    note_content = input("Enter your new note: ").strip()
    if note_content: # Check if the note content is not empty after stripping
        notes.append(note_content)
        print("Note added successfully!")
    else:
        print("Note cannot be empty.")

def edit_note(notes):
    """
    Prompts the user to select a note by index and update its content.
    Handles invalid input for index and empty note content.
    """
    view_notes(notes) # Show notes first so the user knows which one to edit
    if not notes: # If view_notes indicated no notes, there's nothing to edit
        return

    try:
        # Get user input for note number and convert to 0-based index
        note_index = int(input("Enter the number of the note to edit: ")) - 1 
        
        # Validate if the index is within the valid range of notes
        if 0 <= note_index < len(notes):
            new_content = input(f"Enter new content for note {note_index + 1}: ").strip()
            if new_content:
                notes[note_index] = new_content
                print("Note updated successfully!")
            else:
                print("Note content cannot be empty. No change made.")
        else:
            print("Invalid note number. Please try again.")
    except ValueError:
        # Catch error if user enters non-integer input
        print("Invalid input. Please enter a number.")

def delete_note(notes):
    """
    Prompts the user to select a note by index and remove it from the list.
    Handles invalid input for index.
    """
    view_notes(notes) # Show notes first so the user knows which one to delete
    if not notes: # If view_notes indicated no notes, there's nothing to delete
        return

    try:
        # Get user input for note number and convert to 0-based index
        note_index = int(input("Enter the number of the note to delete: ")) - 1 
        
        # Validate if the index is within the valid range of notes
        if 0 <= note_index < len(notes):
            # Remove the note at the specified index and store its content
            deleted_note = notes.pop(note_index) 
            print(f"Note '{deleted_note}' deleted successfully!")
        else:
            print("Invalid note number. Please try again.")
    except ValueError:
        # Catch error if user enters non-integer input
        print("Invalid input. Please enter a number.")

def main():
    """
    The main function that runs the note-taking application.
    It loads notes, displays the menu, and handles user choices in a loop.
    """
    notes = load_notes(NOTES_FILE) # Load existing notes when the app starts

    while True:
        display_menu()
        choice = input("Choose an option: ").strip()

        if choice == '1':
            view_notes(notes)
        elif choice == '2':
            add_note(notes)
            save_notes(NOTES_FILE, notes) # Save changes after adding a note
        elif choice == '3':
            edit_note(notes)
            save_notes(NOTES_FILE, notes) # Save changes after editing a note
        elif choice == '4':
            delete_note(notes)
            save_notes(NOTES_FILE, notes) # Save changes after deleting a note
        elif choice == '5':
            print("Exiting Note-Taking App. Goodbye!")
            break # Exit the loop and terminate the program
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main() # Run the main application when the script is executed
