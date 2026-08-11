"""
This script finds duplicate files within a specified directory and its subdirectories.
It first groups files by size, and then for files with the same size, it calculates
their MD5 hash to identify true duplicates.

Usage:
    python duplicate_finder.py <directory_path>

Example:
    python duplicate_finder.py ./my_documents
"""

import os
import hashlib
import sys

def calculate_file_hash(filepath, hash_algorithm="md5", block_size=65536):
    """
    Calculates the hash of a file's content.

    Args:
        filepath (str): The path to the file.
        hash_algorithm (str): The hashing algorithm to use (e.g., "md5", "sha256").
                              Defaults to "md5" for practical speed and common use.
        block_size (int): The size of chunks to read from the file. Larger files
                          are read in blocks to prevent loading the entire file
                          into memory, which is more memory-efficient.

    Returns:
        str: The hexadecimal digest of the file's hash, or None if the file
             cannot be opened or is not found.
    """
    try:
        # Get the hash object based on the chosen algorithm
        if hash_algorithm.lower() == "md5":
            hasher = hashlib.md5()
        elif hash_algorithm.lower() == "sha256":
            hasher = hashlib.sha256()
        else:
            print(f"Error: Unsupported hash algorithm '{hash_algorithm}'. Defaulting to MD5.")
            hasher = hashlib.md5() # Fallback to MD5

        with open(filepath, 'rb') as f: # Open file in binary read mode
            while True:
                chunk = f.read(block_size) # Read file in chunks
                if not chunk:
                    break # End of file
                hasher.update(chunk) # Update the hash with the current chunk
        return hasher.hexdigest() # Return the hexadecimal representation of the hash
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}. Skipping.")
        return None
    except IOError as e:
        print(f"Warning: Could not read file {filepath}: {e}. Skipping.")
        return None

def find_duplicates(directory):
    """
    Finds duplicate files within the specified directory and its subdirectories.
    It first groups files by size, then by hash for efficiency.

    Args:
        directory (str): The root directory to search for duplicate files.

    Returns:
        dict: A dictionary where keys are file hashes and values are lists of
              absolute paths to files that share that hash (i.e., true duplicates).
              Only groups with more than one file are included in the result.
    """
    # Check if the provided directory exists and is a directory
    if not os.path.isdir(directory):
        print(f"Error: Directory not found or is not a directory: {directory}")
        return {}

    # Step 1: Group files by their size.
    # This is an important optimization: files with different sizes cannot be duplicates.
    # {file_size: [filepath1, filepath2, ...]}
    files_by_size = {}

    print(f"Scanning directory: {os.path.abspath(directory)}...")

    # os.walk generates the file names in a directory tree
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # Get the absolute path for consistent comparisons and output
            abs_filepath = os.path.abspath(filepath)
            try:
                file_size = os.path.getsize(abs_filepath)
                if file_size not in files_by_size:
                    files_by_size[file_size] = []
                files_by_size[file_size].append(abs_filepath)
            except OSError as e:
                # Handle cases where a file might be inaccessible or causes an error
                print(f"Warning: Could not get size for {abs_filepath}: {e}. Skipping.")
                continue

    # Step 2: For groups of files that have the same size (potential duplicates),
    # calculate their content hash to confirm if they are true duplicates.
    # {file_hash: [filepath1, filepath2, ...]}
    duplicates_by_hash = {}

    for size, file_list in files_by_size.items():
        # Only process groups with more than one file, as others cannot be duplicates
        if len(file_list) > 1:
            for filepath in file_list:
                file_hash = calculate_file_hash(filepath)
                if file_hash: # Ensure hash calculation was successful
                    if file_hash not in duplicates_by_hash:
                        duplicates_by_hash[file_hash] = []
                    duplicates_by_hash[file_hash].append(filepath)

    # Step 3: Filter the results to include only true duplicate sets.
    # A set is considered duplicate if its hash maps to more than one file path.
    final_duplicates = {
        file_hash: paths
        for file_hash, paths in duplicates_by_hash.items()
        if len(paths) > 1
    }

    return final_duplicates

if __name__ == "__main__":
    # This block executes when the script is run directly from the command line.

    # Check if a directory path was provided as a command-line argument.
    if len(sys.argv) < 2:
        # If no argument is provided, print the usage instructions from the module docstring.
        print(__doc__)
        print("\nPlease provide a directory path as an argument.")
        print("\nExample: python duplicate_finder.py /path/to/your/folder")
        sys.exit(1) # Exit with an error code, indicating incorrect usage.

    # Get the target directory from the first command-line argument.
    target_directory = sys.argv[1]

    print(f"Initiating duplicate file search in: {target_directory}")
    print("=" * 60) # Separator for better readability

    # Call the main function to find duplicates.
    duplicate_files = find_duplicates(target_directory)

    # Display the results.
    if duplicate_files:
        print("\nFound Duplicate Files:")
        print("-" * 25)
        total_duplicate_files = 0
        for file_hash, paths in duplicate_files.items():
            print(f"\nHash: {file_hash}")
            for path in paths:
                print(f"  - {path}")
                total_duplicate_files += 1
        print("\n" + "=" * 60)
        print(f"Summary: Found {total_duplicate_files} duplicate files across {len(duplicate_files)} unique duplicate sets.")
    else:
        print("\nNo duplicate files found.")
    print("=" * 60)
