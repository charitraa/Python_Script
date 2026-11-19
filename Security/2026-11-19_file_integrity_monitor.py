"""
This script functions as a simple File Integrity Monitor.

It scans specified files and directories, calculates their cryptographic hashes
(SHA256 by default), and stores these hashes in a JSON database file.

On subsequent runs, it compares the current hashes of the monitored files
against the stored hashes to detect any additions, modifications, or deletions.

Usage:
  - To initialize the database with the current state of files:
    python integrity_monitor.py init

  - To monitor for changes (after initialization):
    python integrity_monitor.py monitor

Files and directories to be monitored are configured directly within the script.
"""

import os
import hashlib
import json
import sys
import time # Used here to simulate a short pause in example usage

# --- Configuration ---
# Path to the database file where hashes will be stored.
DATABASE_FILE = "file_integrity_monitor_db.json"

# List of files and directories to monitor.
# Add your desired paths here. Both absolute and relative paths are supported.
# For demonstration purposes, this script will create these example paths
# if they don't exist during the 'init' command.
MONITORED_PATHS = [
    "monitor_this_folder", # A folder for demonstration
    "monitor_this_file.txt" # A standalone file for demonstration
]

# --- Hashing Function ---
def calculate_file_hash(filepath, hash_algorithm='sha256', chunk_size=4096):
    """
    Calculates the cryptographic hash of a given file.

    Args:
        filepath (str): The path to the file.
        hash_algorithm (str): The hashing algorithm to use (e.g., 'sha256', 'md5').
        chunk_size (int): The size of chunks to read from the file.

    Returns:
        str: The hexadecimal digest of the file's hash, or None if the file
             cannot be read or does not exist.
    """
    if not os.path.exists(filepath):
        return None

    try:
        hasher = hashlib.new(hash_algorithm)
        with open(filepath, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError as e:
        print(f"Error reading file {filepath}: {e}")
        return None

# --- Database Management ---
def load_database(db_path):
    """
    Loads the integrity database from a JSON file.

    Args:
        db_path (str): The path to the database file.

    Returns:
        dict: A dictionary where keys are absolute file paths and values are
              their stored hashes. Returns an empty dictionary if the file
              does not exist or is invalid.
    """
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON database '{db_path}': {e}")
            print("Starting with an empty database. Consider re-initializing.")
            return {}
    return {}

def save_database(db_path, database):
    """
    Saves the integrity database to a JSON file.

    Args:
        db_path (str): The path to the database file.
        database (dict): The dictionary containing file paths and their hashes.
    """
    try:
        with open(db_path, 'w') as f:
            # Use indent for pretty-printing the JSON
            json.dump(database, f, indent=4)
    except IOError as e:
        print(f"Error writing database to '{db_path}': {e}")

# --- Monitoring Logic ---
def monitor_integrity(paths_to_monitor, current_hashes_db):
    """
    Scans the specified paths, compares current file hashes with the database,
    and reports any changes.

    Args:
        paths_to_monitor (list): A list of file or directory paths to check.
        current_hashes_db (dict): The dictionary of previously stored file hashes.

    Returns:
        tuple: (new_hashes_db, changes_detected)
               - new_hashes_db (dict): The updated dictionary of hashes after the scan,
                                       representing the *current* state.
               - changes_detected (bool): True if any changes were found, False otherwise.
    """
    print(f"\n--- Scanning {len(paths_to_monitor)} configured paths ---")
    changes_detected = False
    fresh_hashes_db = {} # This will store the hashes of files found in the current scan
    monitored_files_found = set() # To keep track of all absolute paths found during this scan

    for path in paths_to_monitor:
        if not os.path.exists(path):
            # If a top-level monitored path does not exist, it's a warning.
            # We can't hash it, so we skip it for current hash generation.
            print(f"WARNING: Configured path '{path}' does not exist.")
            continue

        # os.path.abspath() is crucial for consistent keys in the database
        # regardless of how paths are specified in MONITORED_PATHS.
        if os.path.isfile(path):
            absolute_path = os.path.abspath(path)
            monitored_files_found.add(absolute_path)

            current_file_hash = calculate_file_hash(absolute_path)
            if current_file_hash is None:
                print(f"  [ERROR] Skipping '{absolute_path}' due to read error.")
                continue

            fresh_hashes_db[absolute_path] = current_file_hash

            if absolute_path not in current_hashes_db:
                print(f"  [NEW] file: '{absolute_path}'")
                changes_detected = True
            elif current_hashes_db[absolute_path] != current_file_hash:
                print(f"  [MODIFIED] file: '{absolute_path}'")
                changes_detected = True
            # else: no change, do nothing
        elif os.path.isdir(path):
            # Walk through the directory to find all files recursively
            for root, _, files in os.walk(path):
                for file_name in files:
                    filepath = os.path.join(root, file_name)
                    absolute_path = os.path.abspath(filepath)
                    monitored_files_found.add(absolute_path)

                    current_file_hash = calculate_file_hash(absolute_path)
                    if current_file_hash is None:
                        print(f"  [ERROR] Skipping '{absolute_path}' due to read error.")
                        continue

                    fresh_hashes_db[absolute_path] = current_file_hash

                    if absolute_path not in current_hashes_db:
                        print(f"  [NEW] file: '{absolute_path}'")
                        changes_detected = True
                    elif current_hashes_db[absolute_path] != current_file_hash:
                        print(f"  [MODIFIED] file: '{absolute_path}'")
                        changes_detected = True
                    # else: no change, do nothing
        else:
            print(f"WARNING: Monitored path '{path}' is not a regular file or directory (e.g., symlink, device). Skipping.")

    # Check for deleted files from the previous database state
    # Iterate over keys from the *old* database to see which ones are no longer found
    for stored_path in current_hashes_db:
        if stored_path not in monitored_files_found:
            # This file was in the previous database but wasn't found in the current scan.
            # It's considered deleted.
            print(f"  [DELETED] file: '{stored_path}'")
            changes_detected = True

    return fresh_hashes_db, changes_detected

# --- Main Execution ---
if __name__ == "__main__":
    # Example usage:
    #   python integrity_monitor.py init    (to initialize the database)
    #   python integrity_monitor.py monitor (to check for changes)

    if len(sys.argv) < 2:
        print("Usage: python integrity_monitor.py [init|monitor]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "init":
        print("\n--- Initializing File Integrity Database ---")
        print("Ensuring example paths exist for demonstration...")
        # Create example directories/files for the first run demonstration
        if not os.path.exists("monitor_this_folder"):
            os.makedirs("monitor_this_folder")
            with open("monitor_this_folder/example_1.txt", "w") as f:
                f.write("This is an example file.")
            with open("monitor_this_folder/example_2.txt", "w") as f:
                f.write("Another file here.")
        if not os.path.exists("monitor_this_file.txt"):
            with open("monitor_this_file.txt", "w") as f:
                f.write("This is a standalone file.")

        # Scan all paths and store their initial hashes.
        # For initial setup, `current_hashes_db` is empty as we're building it.
        initial_hashes, _ = monitor_integrity(MONITORED_PATHS, {})
        save_database(DATABASE_FILE, initial_hashes)
        print(f"\nDatabase initialized successfully at '{DATABASE_FILE}' with {len(initial_hashes)} files monitored.")
        print("\n--- Next Steps ---")
        print("1. Make some changes (add, modify, delete files) in the monitored paths.")
        print("2. Run the monitor command to detect changes:")
        print("   python integrity_monitor.py monitor")

    elif command == "monitor":
        print("\n--- Monitoring File Integrity ---")
        current_hashes_db = load_database(DATABASE_FILE)

        if not current_hashes_db:
            print("ERROR: Database is empty or does not exist.")
            print("Please run 'python integrity_monitor.py init' first to initialize the database.")
            sys.exit(1)

        new_hashes_db, changes_found = monitor_integrity(MONITORED_PATHS, current_hashes_db)

        if changes_found:
            print("\n!!! INTEGRITY CHANGES DETECTED !!!")
            # Save the new state to the database for the next run
            save_database(DATABASE_FILE, new_hashes_db)
            print(f"Database updated at '{DATABASE_FILE}' with the latest state.")
        else:
            print("\nNo integrity changes detected.")
            # If no changes, the database is already current, so no need to save.

    else:
        print(f"Unknown command: '{command}'")
        print("Usage: python integrity_monitor.py [init|monitor]")
        sys.exit(1)
