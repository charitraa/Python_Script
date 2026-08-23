import os
import sys

"""
This script prints the directory tree structure of a specified path.

It takes an optional command-line argument for the directory path.
If no path is provided, it defaults to the current directory.
The output uses ASCII characters to visually represent files and subdirectories,
making it easy to visualize the folder hierarchy.
"""

def print_tree(directory_path, indent=""):
    """
    Recursively prints the directory tree structure starting from `directory_path`.

    Args:
        directory_path (str): The path to the directory to start listing from.
        indent (str): The current indentation string, used for formatting
                      subdirectories and files to create the tree structure.
    """
    
    try:
        # Get all items (files and directories) in the current directory.
        # Sort them alphabetically for consistent and readable output.
        items = sorted(os.listdir(directory_path))
    except PermissionError:
        # Handle cases where the script doesn't have permission to read a directory.
        print(f"{indent}├── [Permission Denied]")
        return
    except Exception as e:
        # Catch other potential errors during directory listing (e.g., path no longer exists).
        print(f"{indent}├── [Error listing: {e}]")
        return

    # Iterate through each item found in the directory
    for i, item in enumerate(items):
        # Determine if the current item is the last one in its parent directory.
        # This helps decide whether to use '└── ' (last item) or '├── ' (not last).
        is_last = (i == len(items) - 1)
        
        # Choose the appropriate connector based on whether it's the last item
        connector = "└── " if is_last else "├── "
        
        # Print the current item's name, prefixed by the current indentation and connector
        print(f"{indent}{connector}{item}")
        
        # Construct the full path to the current item
        item_path = os.path.join(directory_path, item)
        
        # Check if the current item is a directory
        if os.path.isdir(item_path):
            # If it's a directory, recursively call print_tree for its contents.
            # The next indent string needs to be adjusted:
            # If the current item (which is a directory) is the last in its parent,
            # its children do not need a vertical line extending from its branch.
            # Otherwise, they do.
            next_indent = indent + ("    " if is_last else "│   ")
            print_tree(item_path, next_indent)

if __name__ == "__main__":
    # Default to the current directory if no command-line argument is provided.
    target_path = "." 
    
    # Check if a directory path was provided as a command-line argument.
    # sys.argv is a list of command-line arguments; sys.argv[0] is the script name.
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    
    # --- Input Validation ---
    # Ensure the provided path actually exists on the filesystem.
    if not os.path.exists(target_path):
        print(f"Error: The specified path '{target_path}' does not exist.")
        sys.exit(1) # Exit the script with an error code to indicate failure.
    
    # Ensure the provided path is indeed a directory, not a file.
    if not os.path.isdir(target_path):
        print(f"Error: The specified path '{target_path}' is not a directory.")
        sys.exit(1) # Exit the script with an error code.

    # Print the name of the root directory being listed.
    # os.path.abspath converts the path to an absolute path (e.g., "." becomes "/home/user/project").
    # os.path.basename then extracts just the directory name (e.g., "project").
    print(os.path.basename(os.path.abspath(target_path)))
    
    # Start printing the directory tree from the target directory's contents.
    print_tree(target_path)
