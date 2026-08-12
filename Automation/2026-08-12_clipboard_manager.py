# clipboard_manager.py

"""
A simple, command-line based clipboard manager that stores a history of copied
text items. It automatically saves new content from the system clipboard and
allows users to view the history and copy past items back to the clipboard.
The history is persisted to a file so it's not lost between sessions.

To run this script, you may need to install the 'pyperclip' library:
pip install pyperclip

On Linux, pyperclip might also require 'xclip' or 'xsel' to be installed:
sudo apt-get install xclip # or xsel
"""

import pyperclip # pip install pyperclip
import time
import os

class ClipboardManager:
    """
    Manages a history of clipboard contents, allowing users to store, view,
    and restore past clipboard items. History is persisted to a file.
    """
    def __init__(self, max_history=10, history_filename="clipboard_history.txt"):
        """
        Initializes the ClipboardManager.

        Args:
            max_history (int): The maximum number of items to store in the history.
            history_filename (str): The name of the file to store the history.
        """
        self.max_history = max_history
        self.history_filename = history_filename
        self.history = []
        self._load_history_from_file() # Load history when manager starts

    def _save_history_to_file(self):
        """
        Saves the current history to the specified file.
        Each item is stored on a new line. The most recent items are at the top.
        """
        try:
            with open(self.history_filename, 'w', encoding='utf-8') as f:
                for item in self.history:
                    f.write(item + '\n')
        except IOError as e:
            print(f"Error saving history to {self.history_filename}: {e}")

    def _load_history_from_file(self):
        """
        Loads history from the specified file.
        Each line in the file is considered a history item.
        Items are added to maintain MRU order (newest first) and uniqueness.
        """
        if not os.path.exists(self.history_filename):
            return

        try:
            with open(self.history_filename, 'r', encoding='utf-8') as f:
                # Read raw lines, strip whitespace (including newlines), and filter out empty strings
                raw_lines = [line.strip() for line in f if line.strip()]

            # Build a list of unique items, maintaining the order they appeared in the file (newest first).
            # This handles cases where items might have been duplicated in the file.
            loaded_unique_history = []
            for item in raw_lines:
                if item not in loaded_unique_history:
                    loaded_unique_history.append(item)
            
            # Assign the loaded and unique history, trimming it to max_history
            self.history = loaded_unique_history[:self.max_history]

        except IOError as e:
            print(f"Error loading history from {self.history_filename}: {e}")
            self.history = [] # Clear history on error to prevent bad state
        except Exception as e:
            print(f"An unexpected error occurred while loading history: {e}")
            self.history = [] # Clear history on error

    def add_item(self, text):
        """
        Adds a new text item to the clipboard history.
        If the item already exists, it's moved to the front (most recent).
        History is trimmed to `max_history`.

        Args:
            text (str): The text content to add to the history.

        Returns:
            bool: True if an item was added/moved, False otherwise (e.g., empty text).
        """
        if not text or not text.strip(): # Ignore empty or whitespace-only items
            return False # Indicate no item was added

        # If item already exists, remove it to re-add at the front (MRU behavior)
        if text in self.history:
            self.history.remove(text)

        # Add the new item to the front of the list
        self.history.insert(0, text)

        # Trim the history to the maximum allowed size
        self.history = self.history[:self.max_history]
        self._save_history_to_file() # Save changes immediately
        return True # Indicate an item was added

    def get_history_display(self):
        """
        Returns a formatted string of the current history for display.
        """
        if not self.history:
            return "Clipboard history is empty."

        display_lines = ["\n--- Clipboard History ---"]
        for i, item in enumerate(self.history):
            # Truncate long items for display and replace newlines with a symbol for readability
            display_item = item if len(item) < 80 else item[:77] + "..."
            display_lines.append(f"  {i+1}. {display_item.replace('\\n', '↵')}")
        display_lines.append("-------------------------")
        return "\n".join(display_lines)

    def load_item_to_clipboard(self, index):
        """
        Retrieves an item from history by its 1-based index and copies it
        back to the system clipboard. Also moves the item to the front of history (MRU).

        Args:
            index (int): The 1-based index of the item in the history.

        Returns:
            str or None: The copied item text if successful, None otherwise.
        """
        try:
            # Adjust to 0-based index for list access
            item_index = index - 1
            if 0 <= item_index < len(self.history):
                selected_item = self.history[item_index]
                pyperclip.copy(selected_item)
                self.add_item(selected_item) # Move to front of history (MRU)
                return selected_item
            else:
                print("Invalid history item number.")
                return None
        except pyperclip.PyperclipException as e:
            print(f"Error copying to clipboard: {e}. Please ensure a clipboard utility is installed and running.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def clear_history(self):
        """
        Clears all items from the history.
        """
        self.history = []
        self._save_history_to_file() # Save empty history
        print("Clipboard history cleared.")


if __name__ == "__main__":
    # --- Clipboard Manager Example Usage ---

    # 1. Initialize the ClipboardManager
    #    It will try to load history from 'my_clipboard_history.txt' if it exists.
    manager = ClipboardManager(max_history=10, history_filename="my_clipboard_history.txt")

    print("--- Welcome to the Simple Clipboard Manager ---")
    print("This script will monitor your clipboard and store new items.")
    print("You can interact with the history via the menu options.")

    # Get the initial clipboard content to avoid adding it as "new" if it hasn't changed
    # Also, handle potential pyperclip errors during initial access.
    try:
        last_clipboard_content = pyperclip.paste()
        if last_clipboard_content.strip():
            manager.add_item(last_clipboard_content) # Add initial content if not empty
    except pyperclip.PyperclipException as e:
        print(f"\n[WARNING: Clipboard access issue: {e}. Functionality will be limited.]")
        print("  On Linux, you might need 'xclip' or 'xsel': sudo apt-get install xclip / xsel")
        last_clipboard_content = "" # Set to empty if error, to allow re-detecting later
    except Exception as e:
        print(f"\n[WARNING: An unexpected error occurred on initial clipboard access: {e}]")
        last_clipboard_content = ""

    polling_interval = 1.0 # Check clipboard every 1 second

    while True:
        # --- Clipboard Polling ---
        # Check if the clipboard content has changed since the last check.
        # This occurs at the beginning of each loop iteration.
        try:
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != last_clipboard_content:
                # If content changed, try to add it to history.
                # manager.add_item returns True if an item was actually added/moved (i.e., not empty).
                if manager.add_item(current_clipboard_content):
                    print(f"\n[New item added from clipboard: '{current_clipboard_content[:50].replace('\\n', '↵')}...']\n")
                last_clipboard_content = current_clipboard_content # Update regardless of whether it was added
        except pyperclip.PyperclipException as e:
            print(f"\n[Clipboard access error during polling: {e}. Please ensure a clipboard utility is running.]")
            # If there's an error, assume content is unknown, reset last_clipboard_content to empty
            # so that when clipboard access is restored, new content is detected.
            last_clipboard_content = ""
        except Exception as e:
            print(f"\n[An unexpected error occurred during clipboard paste polling: {e}]")
            last_clipboard_content = ""


        # --- Display Menu & Get User Input ---
        print("\n--- Clipboard Manager Menu ---")
        print("1. View History")
        print("2. Select and Copy Item to Clipboard")
        print("3. Clear History")
        print("4. Exit")
        print(f"\n(Monitoring clipboard every {polling_interval} second(s) for changes.)")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            # View History
            print(manager.get_history_display())
        elif choice == '2':
            # Select and Copy Item
            print(manager.get_history_display())
            if manager.history: # Only ask for input if history is not empty
                try:
                    item_number = int(input("Enter the number of the item to copy back to clipboard: "))
                    selected_item = manager.load_item_to_clipboard(item_number)
                    if selected_item:
                        print(f"Copied '{selected_item[:50].replace('\\n', '↵')}...' back to clipboard.")
                        # It's important to update last_clipboard_content here so the script
                        # doesn't immediately re-add the item *it just copied* as a "new" item.
                        last_clipboard_content = selected_item
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("History is empty. Nothing to select.")
        elif choice == '3':
            # Clear History
            confirm = input("Are you sure you want to clear all history? (yes/no): ").strip().lower()
            if confirm == 'yes':
                manager.clear_history()
            else:
                print("History clear cancelled.")
        elif choice == '4':
            # Exit
            print("Exiting Clipboard Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

        # Pause before next iteration to prevent busy-waiting and reduce CPU usage.
        # This makes the polling happen at a controlled rate.
        time.sleep(polling_interval)
