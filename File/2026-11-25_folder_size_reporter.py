"""
A Python script to report the total size of a given folder, including all its subfolders and files.
It can be run without arguments to report the current directory's size,
or with a directory path as an argument.
The size is displayed in a human-readable format (e.g., KB, MB, GB).
"""

import os
import sys

def convert_bytes_to_human_readable(size_bytes):
    """
    Converts a size in bytes into a human-readable format (B, KB, MB, GB, TB).

    Args:
        size_bytes (int): The size in bytes.

    Returns:
        str: A string representing the size in a human-readable format.
    """
    if size_bytes == 0:
        return "0 Bytes"

    # Define units and their corresponding powers of 1024
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    
    # Determine the appropriate unit by repeatedly dividing by 1024
    # until the size is less than 1024 or we run out of units.
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1

    # Format the number to two decimal places for readability
    return f"{size_bytes:.2f} {units[i]}"


def get_folder_size(path):
    """
    Calculates the total size of a folder, including all files and subfolders.

    Args:
        path (str): The path to the folder.

    Returns:
        int: The total size of the folder in bytes. Returns 0 if the path
             does not exist or is not a directory, or if there are
             permission errors preventing size calculation.
    """
    total_size = 0
    
    # Validate the provided path
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return 0
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' is not a directory.")
        # If it's a file, this script is designed for folders, so we return 0.
        return 0

    # os.walk() generates the file names in a directory tree by walking the tree either top-down or bottom-up.
    # For each directory in the tree rooted at 'path' (including 'path' itself),
    # it yields a 3-tuple: (dirpath, dirnames, filenames).
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            # Iterate over all files found in the current directory (dirpath)
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                # Check if the path is a symbolic link.
                # Skipping symbolic links prevents infinite loops (if a link points to a parent directory)
                # and avoids counting files that are physically located outside the target folder's tree.
                if not os.path.islink(file_path):
                    try:
                        # Add the size of the current file to the total
                        total_size += os.path.getsize(file_path)
                    except OSError as e:
                        # Catch specific OS errors (e.g., PermissionError for a single file)
                        # and print a warning, but continue processing other files.
                        print(f"Warning: Could not get size of '{file_path}': {e}")
    except PermissionError as e:
        # Catch permission errors that prevent os.walk from entering a directory.
        # In this case, we cannot calculate the full size, so we print an error and return 0.
        print(f"Error: Permission denied for folder '{path}'. Cannot calculate full size. {e}")
        return 0 
    except Exception as e:
        # Catch any other unexpected errors during the walk process.
        print(f"An unexpected error occurred while processing '{path}': {e}")
        return 0

    return total_size


if __name__ == "__main__":
    # The script can be run with an optional command-line argument for the folder path.
    # Example usage:
    #   python folder_size_reporter.py
    #   python folder_size_reporter.py /path/to/your/folder
    #   python folder_size_reporter.py . (for current directory)
    #   python folder_size_reporter.py .. (for parent directory)

    if len(sys.argv) > 1:
        # If an argument is provided, use it as the target path.
        target_path = sys.argv[1]
    else:
        # If no argument is provided, default to the current working directory.
        target_path = "."  

    # Print the absolute path of the target for clarity.
    print(f"Calculating size for: '{os.path.abspath(target_path)}'...")

    # Get the total size of the folder in bytes.
    size_in_bytes = get_folder_size(target_path)

    # Only print the result if a valid size was calculated (i.e., not 0 due to errors).
    if size_in_bytes > 0: 
        # Convert the bytes to a human-readable format.
        human_readable_size = convert_bytes_to_human_readable(size_in_bytes)
        print(f"Total size: {human_readable_size}")
    elif size_in_bytes == 0 and os.path.exists(target_path) and os.path.isdir(target_path):
        # This condition handles cases where the folder genuinely exists and is a directory,
        # but its total content size is 0 bytes (e.g., an empty folder or only contains empty files/folders
        # it couldn't access, but no errors prevented starting the scan).
        print("Total size: 0 Bytes (or couldn't access any files)")
    # If size_in_bytes is 0 and the above condition is false, it means an error message
    # was already printed by get_folder_size (e.g., path does not exist, not a directory, or permission error).
