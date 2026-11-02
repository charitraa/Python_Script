"""
This script provides a simple DictionaryLookup tool using a Python class.
It allows users to store, retrieve, update, and delete key-value pairs (like words and their definitions).
It's designed to be beginner-friendly, demonstrating basic dictionary operations within a class structure.
"""

class DictionaryLookup:
    """
    A simple dictionary lookup tool to manage key-value pairs.

    Attributes:
        data (dict): The internal dictionary storing the key-value pairs.
    """

    def __init__(self, initial_data=None):
        """
        Initializes the DictionaryLookup with an optional initial dictionary.

        Args:
            initial_data (dict, optional): A dictionary to pre-populate the lookup tool.
                                           Defaults to an empty dictionary.
        """
        # Ensure initial_data is a dictionary, or default to an empty one
        self.data = dict(initial_data) if initial_data is not None else {}
        print("DictionaryLookup initialized.")

    def add_entry(self, key, value):
        """
        Adds a new key-value pair to the dictionary.
        If the key already exists, its value will be updated.

        Args:
            key: The key to add or update.
            value: The value associated with the key.
        """
        if key in self.data:
            print(f"'{key}' already exists. Updating its value from '{self.data[key]}' to '{value}'.")
        else:
            print(f"Adding new entry: '{key}': '{value}'")
        self.data[key] = value

    def get_value(self, key):
        """
        Retrieves the value associated with a given key.

        Args:
            key: The key to look up.

        Returns:
            The value associated with the key if found, otherwise None.
            Prints an error message if the key is not found.
        """
        if key in self.data:
            print(f"Found '{key}': '{self.data[key]}'")
            return self.data[key]
        else:
            print(f"Error: Key '{key}' not found in the dictionary.")
            return None # Returning None is a common way to indicate absence when an item is not found

    def update_entry(self, key, new_value):
        """
        Updates the value of an existing key.
        If the key does not exist, it prints an error message.

        Args:
            key: The key to update.
            new_value: The new value for the key.
        """
        if key in self.data:
            old_value = self.data[key]
            self.data[key] = new_value
            print(f"Updated '{key}' from '{old_value}' to '{new_value}'.")
        else:
            print(f"Error: Cannot update. Key '{key}' not found in the dictionary.")

    def delete_entry(self, key):
        """
        Deletes a key-value pair from the dictionary.
        If the key does not exist, it prints an error message.

        Args:
            key: The key to delete.
        """
        if key in self.data:
            value = self.data.pop(key) # dict.pop() removes the key and returns its value
            print(f"Deleted entry: '{key}': '{value}'.")
        else:
            print(f"Error: Cannot delete. Key '{key}' not found in the dictionary.")

    def has_key(self, key):
        """
        Checks if a key exists in the dictionary.

        Args:
            key: The key to check for existence.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        exists = key in self.data
        print(f"Does key '{key}' exist? {exists}")
        return exists

    def list_all_entries(self):
        """
        Prints all key-value pairs currently stored in the dictionary.
        If the dictionary is empty, it prints a corresponding message.
        """
        print("\n--- All Dictionary Entries ---")
        if not self.data:
            print("The dictionary is currently empty.")
        else:
            # Iterate through the dictionary and print each key-value pair
            for key, value in self.data.items():
                print(f"  '{key}': '{value}'")
        print("------------------------------")


if __name__ == "__main__":
    # --- Example Usage ---

    print("--- Initializing the Dictionary Lookup Tool ---")
    # Initialize the tool with some pre-defined entries
    my_dictionary = DictionaryLookup(initial_data={
        "apple": "A round fruit with crisp flesh and green or red skin.",
        "banana": "A long curved fruit which grows in clusters and has soft pulpy flesh and yellow skin when ripe.",
        "orange": "A round juicy citrus fruit with a tough bright reddish-yellow rind."
    })

    my_dictionary.list_all_entries()

    print("\n--- Testing 'get_value' ---")
    my_dictionary.get_value("apple")
    my_dictionary.get_value("grape") # Non-existent key

    print("\n--- Testing 'add_entry' ---")
    my_dictionary.add_entry("grape", "A berry, typically green, purple, or red, growing in clusters.")
    my_dictionary.add_entry("apple", "A common pome fruit, produced by the apple tree.") # Update existing entry
    my_dictionary.list_all_entries()

    print("\n--- Testing 'update_entry' ---")
    my_dictionary.update_entry("banana", "A long, edible fruit, botanically a berry, produced by several kinds of large herbaceous flowering plants.")
    my_dictionary.update_entry("kiwi", "A fuzzy brown fruit with green flesh.") # Attempt to update non-existent key

    my_dictionary.list_all_entries()

    print("\n--- Testing 'has_key' ---")
    my_dictionary.has_key("orange")
    my_dictionary.has_key("melon") # Non-existent key

    print("\n--- Testing 'delete_entry' ---")
    my_dictionary.delete_entry("orange")
    my_dictionary.delete_entry("pear") # Attempt to delete non-existent key

    my_dictionary.list_all_entries()

    print("\n--- Testing 'get_value' again after deletion ---")
    my_dictionary.get_value("orange") # Should now report not found

    print("\n--- Adding more entries and listing all ---")
    my_dictionary.add_entry("pear", "A sweet, juicy, edible fruit, typically rounded but tapering toward the stem, with a soft, slightly gritty flesh.")
    my_dictionary.add_entry("mango", "A fleshy, oval, yellowish-red tropical fruit.")
    my_dictionary.list_all_entries()
