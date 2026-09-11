"""
This script demonstrates how a JSON file can be used as a simple, file-based database.
It provides a `JSONDatabase` class that encapsulates common database operations
like creating, reading, updating, and deleting records.

Each "record" in this database is a key-value pair, where the key is a unique string
(acting as a record ID) and the value is a dictionary containing the record's data.

**Key Concepts Illustrated:**
-   **Persistence:** Data is saved to a JSON file on disk and reloaded when the database
    is initialized, ensuring data persists between program runs.
-   **CRUD Operations:** Basic Create, Read, Update, Delete functionality.
-   **Serialization/Deserialization:** Using Python's `json` module to convert Python
    dictionaries to JSON strings (serialization) and back (deserialization).
-   **Error Handling:** Basic handling for file not found or malformed JSON files.

**Limitations (inherent to JSON as a simple database):**
-   **Concurrency:** Not suitable for multiple simultaneous writers without complex locking mechanisms.
    A simple JSON file is prone to race conditions and data corruption if multiple
    processes try to write to it concurrently.
-   **Scalability:** Performance degrades rapidly with very large datasets as the entire
    file must often be read into memory.
-   **Querying:** Limited to simple key lookups. Complex queries (e.g., "find all users
    older than 30") would require manually iterating through all records in memory.
-   **Data Integrity:** No built-in schema validation or transaction support.

This approach is best suited for small-scale applications, configuration files,
or personal projects where simplicity and ease of use outweigh the need for
advanced database features.
"""

import json
import os

class JSONDatabase:
    """
    A simple file-based JSON database for storing key-value pairs.
    Each 'record' is identified by a unique string key (record_id)
    and stores a dictionary as its value.
    Data is loaded from and saved to a specified JSON file.
    """

    def __init__(self, db_file):
        """
        Initializes the JSONDatabase.
        Loads existing data from the given file or starts with an empty database.

        Args:
            db_file (str): The path to the JSON file to use as the database.
        """
        self.db_file = db_file
        self._data = {}  # In-memory dictionary to hold the database content
        self._load_data()

    def _load_data(self):
        """
        Loads data from the JSON file into the in-memory _data dictionary.
        Handles cases where the file doesn't exist or is malformed.
        """
        # Check if the database file exists
        if not os.path.exists(self.db_file):
            print(f"Database file '{self.db_file}' not found. Starting with an empty database.")
            # If the file doesn't exist, the in-memory database remains empty
            return

        try:
            # Open the file in read mode ('r') and load its JSON content
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            print(f"Data loaded successfully from '{self.db_file}'.")
        except json.JSONDecodeError:
            # Handle cases where the JSON file is not valid
            print(f"Warning: Database file '{self.db_file}' is malformed. Starting with an empty database.")
            self._data = {} # Reset data if file is corrupt
        except Exception as e:
            # Catch other potential file I/O errors
            print(f"Error loading database from '{self.db_file}': {e}. Starting with an empty database.")
            self._data = {}

    def _save_data(self):
        """
        Saves the current in-memory _data dictionary to the JSON file.
        Pretty prints the JSON for human readability.
        """
        try:
            # Open the file in write mode ('w'). This will create the file if it doesn't exist,
            # or overwrite it if it does.
            with open(self.db_file, 'w', encoding='utf-8') as f:
                # Use json.dump to write the Python dictionary to the file as JSON.
                # 'indent=4' makes the JSON output human-readable with 4 spaces indentation.
                # 'ensure_ascii=False' allows non-ASCII characters to be stored directly.
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            print(f"Data saved successfully to '{self.db_file}'.")
        except Exception as e:
            print(f"Error saving database to '{self.db_file}': {e}")

    def create(self, record_id, record_data):
        """
        Creates a new record with the given record_id and data.

        Args:
            record_id (str): A unique identifier for the record.
            record_data (dict): A dictionary representing the record's content.
                                This must be JSON-serializable.

        Returns:
            bool: True if the record was created, False if record_id already exists
                  or inputs are invalid.
        """
        if not isinstance(record_id, str):
            print("Error: record_id must be a string.")
            return False
        if not isinstance(record_data, dict):
            print("Error: record_data must be a dictionary.")
            return False

        if record_id in self._data:
            print(f"Error: Record with ID '{record_id}' already exists. Cannot create.")
            return False
        
        # Add the new record to the in-memory dictionary
        self._data[record_id] = record_data
        self._save_data() # Persist the changes to the file immediately
        print(f"Record '{record_id}' created.")
        return True

    def read(self, record_id):
        """
        Reads and returns the record associated with the given record_id.

        Args:
            record_id (str): The unique identifier of the record to retrieve.

        Returns:
            dict or None: The record's data if found, otherwise None.
        """
        if record_id not in self._data:
            print(f"Error: Record with ID '{record_id}' not found.")
            return None
        
        print(f"Record '{record_id}' read.")
        # Use .get() for safer access, though `if record_id not in self._data` already handles it.
        return self._data.get(record_id)

    def update(self, record_id, new_data):
        """
        Updates an existing record with new data.
        The `new_data` dictionary will be merged into the existing record.
        Existing fields will be overwritten, new fields added.

        Args:
            record_id (str): The unique identifier of the record to update.
            new_data (dict): A dictionary containing the new data for the record.

        Returns:
            bool: True if the record was updated, False if record_id not found
                  or new_data is invalid.
        """
        if not isinstance(record_id, str):
            print("Error: record_id must be a string.")
            return False
        if not isinstance(new_data, dict):
            print("Error: new_data must be a dictionary.")
            return False

        if record_id not in self._data:
            print(f"Error: Record with ID '{record_id}' not found for update.")
            return False
        
        # Update the existing dictionary for the record_id.
        # This merges new_data into the existing record, overwriting shared keys
        # and adding new ones.
        self._data[record_id].update(new_data)
        self._save_data() # Persist the changes
        print(f"Record '{record_id}' updated.")
        return True

    def delete(self, record_id):
        """
        Deletes the record associated with the given record_id.

        Args:
            record_id (str): The unique identifier of the record to delete.

        Returns:
            bool: True if the record was deleted, False if record_id not found.
        """
        if record_id not in self._data:
            print(f"Error: Record with ID '{record_id}' not found for deletion.")
            return False
        
        # Remove the record from the in-memory dictionary
        del self._data[record_id]
        self._save_data() # Persist the changes
        print(f"Record '{record_id}' deleted.")
        return True

    def get_all(self):
        """
        Retrieves all records currently in the database.

        Returns:
            dict: A dictionary containing all record_id-record_data pairs.
                  A copy is returned to prevent direct modification of the
                  internal database state from outside the class.
        """
        print("Retrieving all records.")
        return self._data.copy()

    def count(self):
        """
        Returns the number of records in the database.
        """
        return len(self._data)

if __name__ == "__main__":
    DB_FILE_NAME = "my_simple_database.json"

    # --- Cleanup previous run's database file if it exists ---
    # This ensures a clean slate for each demonstration run.
    if os.path.exists(DB_FILE_NAME):
        os.remove(DB_FILE_NAME)
        print(f"Cleaned up '{DB_FILE_NAME}' from previous runs.")

    print("\n--- Initializing Database ---")
    # Create an instance of our JSON database
    db = JSONDatabase(DB_FILE_NAME)

    print("\n--- Creating Records ---")
    # Add some records
    db.create("user1", {"name": "Alice", "email": "alice@example.com", "age": 30})
    db.create("productA", {"name": "Laptop", "price": 1200.50, "in_stock": True})
    db.create("user2", {"name": "Bob", "email": "bob@example.com", "age": 25})
    
    # Attempt to create an existing record (should fail)
    db.create("user1", {"name": "Alicia", "email": "alicia@example.com"})

    print(f"\nTotal records after creation: {db.count()}")
    print("Current database content:")
    # Use json.dumps to pretty-print the dictionary for display
    print(json.dumps(db.get_all(), indent=2, ensure_ascii=False))

    print("\n--- Reading Records ---")
    # Read an existing record
    user1_data = db.read("user1")
    if user1_data:
        print(f"Found user1: {user1_data}")
    
    # Attempt to read a non-existent record (should fail)
    productB_data = db.read("productB") 

    print("\n--- Updating a Record ---")
    # Update an existing record, adding a new field 'city' and changing 'age'
    db.update("user1", {"age": 31, "city": "New York"})
    # Update another record, changing only 'price'
    db.update("productA", {"price": 1150.00, "in_stock": False})
    
    # Attempt to update a non-existent record (should fail)
    db.update("orderX", {"status": "shipped"})

    print(f"\nTotal records after update: {db.count()}")
    print("Current database content:")
    print(json.dumps(db.get_all(), indent=2, ensure_ascii=False))

    print("\n--- Deleting a Record ---")
    # Delete an existing record
    db.delete("user2")
    
    # Attempt to delete a non-existent record (should fail)
    db.delete("user2") # Trying to delete again

    print(f"\nTotal records after deletion: {db.count()}")
    print("Current database content:")
    print(json.dumps(db.get_all(), indent=2, ensure_ascii=False))

    print("\n--- Demonstrating Persistence ---")
    # To show persistence, we'll create a *new* instance of the database class
    # pointing to the *same* file. It should load the data saved by the previous instance.
    print(f"Re-initializing database from '{DB_FILE_NAME}' to demonstrate persistence.")
    new_db_instance = JSONDatabase(DB_FILE_NAME)
    
    print(f"Total records in new instance: {new_db_instance.count()}")
    print("Content in new instance:")
    print(json.dumps(new_db_instance.get_all(), indent=2, ensure_ascii=False))

    print("\n--- Cleaning up the database file ---")
    # It's good practice to clean up files created during examples.
    if os.path.exists(DB_FILE_NAME):
        os.remove(DB_FILE_NAME)
        print(f"Deleted '{DB_FILE_NAME}'.")
    else:
        print(f"'{DB_FILE_NAME}' already deleted.")
