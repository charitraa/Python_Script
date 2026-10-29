import os
import argparse

"""
This script helps you find and optionally delete empty folders starting from a specified directory.

It performs a 'dry run' by default, meaning it will list empty folders without deleting them.
To actually delete the folders, you need to use the '--delete' flag.

Usage:
    # Dry run: Find empty folders in the current directory and its subdirectories
    python empty_folder_cleaner.py

    # Dry run: Find empty folders in a specific directory (e.g., '/home/user/downloads')
    python empty_folder_cleaner.py /home/user/downloads

    # Delete empty folders in the current directory and its subdirectories (USE WITH CAUTION!)
    python empty_folder_cleaner.py --delete

    # Delete empty folders in a specific directory (e.g., '/home/user/temp') (USE WITH CAUTION!)
    python empty_folder_cleaner.py /home/user/temp --delete
"""

def clean_empty_folders(root_path, delete_mode=False):
    """
    Finds and optionally deletes empty folders within a specified root path.

    Args:
        root_path (str): The starting directory to scan.
        delete_mode (bool): If True, empty folders will be deleted.
                            If False (default), it will only list them (dry run).

    Returns:
        int: The total count of empty folders found/deleted.
    """
    # Check if the provided root_path is a valid directory
    if not os.path.isdir(root_path):
        print(f"Error: The provided path '{root_path}' is not a valid directory.")
        return 0

    print(f"Scanning for empty folders in: '{os.path.abspath(root_path)}'")

    # Inform the user about the mode of operation
    if not delete_mode:
        print("\n--- Running in DRY RUN mode. No folders will be deleted. ---")
        print("To delete folders, run the script with the '--delete' flag.")
    else:
        print("\n--- Running in DELETE mode. Empty folders will be permanently removed. ---")
        user_confirm = input("Are you sure you want to proceed? This action is irreversible! (yes/no): ").lower()
        if user_confirm != 'yes':
            print("Operation cancelled by user.")
            return 0

    found_count = 0
    deleted_count = 0
    errors_count = 0

    # os.walk(topdown=False) is crucial here. It traverses the directory tree
    # from the bottom up (i.e., it processes subdirectories before their parents).
    # This ensures that if a subdirectory becomes empty after its contents are removed,
    # its parent directory can then correctly be identified as empty (if applicable)
    # and also be deleted in a subsequent step.
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        try:
            # os.listdir() returns a list of all entries (files and directories)
            # in the given path. If the list is empty, the directory is truly empty.
            # This accounts for hidden files as well; if it contains *any* entry,
            # os.listdir() will not return an empty list.
            if not os.listdir(dirpath):
                # Ensure we don't try to delete the initial root_path provided by the user.
                # It's an important safeguard against accidental deletion of the starting point.
                if os.path.abspath(dirpath) == os.path.abspath(root_path):
                    # Notify if the root directory itself is empty but won't be deleted.
                    print(f"  Note: The root directory '{dirpath}' is empty, but will not be deleted.")
                    continue # Skip to the next directory
                
                found_count += 1
                print(f"  Empty folder found: '{dirpath}'")

                if delete_mode:
                    try:
                        os.rmdir(dirpath) # Attempt to remove the empty directory
                        deleted_count += 1
                        print(f"    Deleted: '{dirpath}'")
                    except OSError as e:
                        # This can happen if, between checking with os.listdir() and calling os.rmdir(),
                        # another process created a file in the directory, or if there are permission issues.
                        errors_count += 1
                        print(f"    Error deleting '{dirpath}': {e}")
            
        except PermissionError:
            errors_count += 1
            print(f"  Permission denied: Could not access '{dirpath}'. Skipping.")
        except FileNotFoundError:
            # This can happen if a directory was already deleted (e.g., by a previous iteration
            # of the bottom-up walk, or by another process running concurrently).
            # No action needed, it's already gone.
            pass
        except Exception as e:
            # Catch any other unexpected errors
            errors_count += 1
            print(f"  An unexpected error occurred with '{dirpath}': {e}")

    print("\n--- Scan Complete ---")
    print(f"Total empty folders found: {found_count}")
    if delete_mode:
        print(f"Total empty folders deleted: {deleted_count}")
        if errors_count > 0:
            print(f"Warning: {errors_count} errors encountered. Some folders might not have been deleted.")
    else:
        print("No folders were deleted (dry run mode).")
        if errors_count > 0:
            print(f"Warning: {errors_count} errors encountered during scan.")
    
    return found_count

if __name__ == "__main__":
    # Set up argument parsing for user-friendly command-line interaction
    parser = argparse.ArgumentParser(
        description="Find and optionally delete empty folders.",
        # RawTextHelpFormatter is used for better control over the description's line breaks.
        formatter_class=argparse.RawTextHelpFormatter 
    )
    
    # Define the 'path' argument. It's optional and defaults to the current directory ('.').
    parser.add_argument(
        "path",
        nargs="?", # Makes the argument optional (0 or 1 occurrence)
        default=".", # Default value if no path is provided
        help="The root directory to start scanning from.\n"
             "Defaults to the current directory ('.')."
    )
    
    # Define the '--delete' flag. If present, it will set args.delete to True.
    parser.add_argument(
        "--delete",
        action="store_true", # This action stores True when the argument is present.
        help="Enable delete mode. Empty folders will be permanently removed.\n"
             "USE WITH EXTREME CAUTION! This action is irreversible."
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the main cleaning function with the parsed arguments
    clean_empty_folders(args.path, args.delete)
