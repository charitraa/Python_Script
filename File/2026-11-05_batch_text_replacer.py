"""
This script provides a utility for batch replacing text in multiple files within a specified directory.
It allows users to find a specific string or regular expression pattern and replace it with new text
across many files, optionally filtering by file extension and ignoring case.

WARNING: Always back up your files before running any script that modifies them in bulk.
This script modifies files directly and does not create backups automatically.
"""

import os
import re
import sys

def replace_in_file(filepath, old_pattern, new_string, ignore_case=False, encoding='utf-8'):
    """
    Replaces occurrences of a given pattern with a new string in a single file.

    Args:
        filepath (str): The path to the file to be modified.
        old_pattern (str): The text pattern (can be a regular expression) to search for.
        new_string (str): The string to replace found patterns with.
        ignore_case (bool): If True, the search will be case-insensitive.
        encoding (str): The character encoding of the file (e.g., 'utf-8', 'latin-1').

    Returns:
        bool: True if replacements were made, False otherwise.
    """
    try:
        # Read the entire content of the file
        # 'errors="ignore"' is used to prevent UnicodeDecodeError for files with
        # unexpected encodings or binary content, allowing the script to proceed
        # without crashing, though it might result in partial or incorrect reading.
        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()

        # Determine the regex flags based on ignore_case
        flags = re.IGNORECASE if ignore_case else 0

        # Perform the replacement using re.sub.
        # old_pattern is treated as a regular expression. If you always want
        # literal string replacement without regex features, you would use
        # `re.escape(old_pattern)` here. For this script, allowing regex
        # patterns provides more flexibility.
        new_content = re.sub(old_pattern, new_string, content, flags=flags)

        # If content has changed, write the new content back to the file
        if new_content != content:
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(new_content)
            return True
        else:
            return False

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return False
    except PermissionError:
        print(f"Error: Permission denied to access file: {filepath}")
        return False
    except Exception as e:
        # Catch any other unexpected errors during file processing
        print(f"An unexpected error occurred while processing {filepath}: {e}")
        return False

def batch_replace(
    directory,
    old_pattern,
    new_string,
    file_extensions=None, # e.g., ['.txt', '.md']
    ignore_case=False,
    encoding='utf-8',
    dry_run=False
):
    """
    Performs a batch text replacement in files within a specified directory and its subdirectories.

    Args:
        directory (str): The root directory to start searching for files.
        old_pattern (str): The text pattern (can be a regular expression) to search for.
        new_string (str): The string to replace found patterns with.
        file_extensions (list of str, optional): A list of file extensions to target
                                                  (e.g., ['.txt', '.md']). If None, all files are processed.
        ignore_case (bool): If True, the search will be case-insensitive.
        encoding (str): The character encoding of the files (e.g., 'utf-8').
        dry_run (bool): If True, no files will be modified; only reports what *would* be done.
    """
    if dry_run:
        print("\n--- DRY RUN MODE --- No files will be modified. ---\n")

    print(f"Starting batch replacement in: {directory}")
    print(f"Searching for: '{old_pattern}'")
    print(f"Replacing with: '{new_string}'")
    if file_extensions:
        # Convert all target extensions to lowercase for case-insensitive matching
        target_extensions = [ext.lower() for ext in file_extensions]
        print(f"Targeting file extensions: {', '.join(target_extensions)}")
    else:
        print("Targeting all files (no extension filter).")
    print(f"Case-insensitive search: {ignore_case}")
    print("-" * 50)

    files_processed = 0
    files_modified = 0

    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for filename in files:
            # Construct the full file path
            filepath = os.path.join(root, filename)

            # Check if the file matches the desired extension (if specified)
            if file_extensions:
                # Get the file extension (e.g., '.txt') and convert to lowercase for comparison
                _, ext = os.path.splitext(filename)
                if ext.lower() not in target_extensions:
                    continue # Skip this file if its extension doesn't match the target list

            print(f"Processing: {filepath}...", end=" ")

            if dry_run:
                # In dry run mode, we only check if a match would be found
                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    flags = re.IGNORECASE if ignore_case else 0
                    if re.search(old_pattern, content, flags=flags):
                        print("MATCH FOUND (would modify)")
                        files_modified += 1
                    else:
                        print("No match.")
                except Exception as e:
                    # Catch errors specific to reading during dry run check
                    print(f"Error during dry run check (could not read file): {e}")
                files_processed += 1
            else:
                # If not dry run, perform the actual replacement
                if replace_in_file(filepath, old_pattern, new_string, ignore_case, encoding):
                    print("MODIFIED")
                    files_modified += 1
                else:
                    print("No change needed.")
                files_processed += 1

    print("-" * 50)
    print(f"Batch replacement finished.")
    print(f"Total files processed: {files_processed}")
    print(f"Files modified: {files_modified}")
    if dry_run:
        print("\n--- This was a DRY RUN. No files were actually changed. ---")
    print("\nRemember to back up your files before making permanent changes!")

if __name__ == "__main__":
    # --- EXAMPLE USAGE ---
    # This block demonstrates how to use the batch_replace function.
    # It creates a temporary directory and some dummy files, runs the replacement,
    # and then cleans up the temporary files.

    # IMPORTANT: Always back up your files before running this script on real data!
    # This example uses a temporary directory to avoid accidental modifications.

    temp_dir = "temp_batch_replace_test"
    # Create the temporary directory if it doesn't already exist
    os.makedirs(temp_dir, exist_ok=True) 

    # Create some dummy files for testing purposes
    print(f"Creating dummy files in '{temp_dir}' for demonstration...")
    file1_content = "Hello world!\nThis is a test file.\nWorld is great.\npython is awesome."
    file2_content = "Python programming.\nPython is powerful.\nTest test test."
    file3_content = "Another document.\nSome other text."
    file4_content = "TEXT file for test.\nAnother text line.\nPython Rocks."
    file5_content = "YAML data:\n  - item: value\n  - python: true"

    # Write content to various dummy files with different extensions
    with open(os.path.join(temp_dir, "file1.txt"), "w", encoding='utf-8') as f:
        f.write(file1_content)
    with open(os.path.join(temp_dir, "document.md"), "w", encoding='utf-8') as f:
        f.write(file2_content)
    with open(os.path.join(temp_dir, "log.txt"), "w", encoding='utf-8') as f:
        f.write(file3_content)
    with open(os.path.join(temp_dir, "report.TXT"), "w", encoding='utf-8') as f: # Different case extension
        f.write(file4_content)
    with open(os.path.join(temp_dir, "config.yaml"), "w", encoding='utf-8') as f:
        f.write(file5_content)
    # Create a binary file that should ideally be skipped or handled by errors='ignore'
    with open(os.path.join(temp_dir, "binary.bin"), "wb") as f:
        f.write(b'\x00\x01\x02\x03\x04') 

    print("Dummy files created.")

    # --- Example 1: Simple string replacement, case-sensitive, specific extension ---
    print("\n" + "="*70)
    print("--- Running Example 1: Replacing 'World' with 'Universe' in .txt files (case-sensitive) ---")
    print("="*70)
    batch_replace(
        directory=temp_dir,
        old_pattern="World",
        new_string="Universe",
        file_extensions=['.txt'], # Target only .txt files
        ignore_case=False,        # Case-sensitive search
        dry_run=False             # Set to True to only preview changes without modifying files
    )

    # --- Example 2: Case-insensitive replacement, multiple extensions ---
    print("\n" + "="*70)
    print("--- Running Example 2: Replacing 'python' with 'Java' in .txt and .md files (case-insensitive) ---")
    print("="*70)
    batch_replace(
        directory=temp_dir,
        old_pattern="python",
        new_string="Java",
        file_extensions=['.txt', '.md'], # Target both .txt and .md files
        ignore_case=True,                 # Case-insensitive search (will match 'python', 'Python', 'PYTHON', etc.)
        dry_run=False                     # Perform actual modifications
    )

    # --- Example 3: Replacing a regex pattern, specific text-based files (dry run) ---
    print("\n" + "="*70)
    print("--- Running Example 3: Replacing 'test\\s+' with 'sample ' in text files (DRY RUN) ---")
    print("="*70)
    # This will search for the literal string "test" followed by one or more whitespace characters
    # (e.g., "test ", "test\t", "test  ") and replace it with "sample ".
    # Note the use of a raw string (r"...") for the regex pattern to avoid issues with backslashes.
    batch_replace(
        directory=temp_dir,
        old_pattern=r"test\s+", 
        new_string="sample ",
        file_extensions=['.txt', '.md', '.yaml'], # Explicitly target common text-based files
        ignore_case=True,                         # Case-insensitive search
        dry_run=True                              # IMPORTANT: This is a dry run, no files will be changed!
    )
    
    # --- Example 4: Attempting to replace a string that doesn't exist ---
    print("\n" + "="*70)
    print("--- Running Example 4: Replacing 'NonExistentWord' with 'Found' (should show no changes) ---")
    print("="*70)
    batch_replace(
        directory=temp_dir,
        old_pattern="NonExistentWord",
        new_string="Found",
        file_extensions=['.txt'],
        dry_run=False
    )

    # --- Cleanup ---
    # Remove the temporary directory and all its contents created for the example.
    print(f"\nCleaning up temporary directory: {temp_dir}...")
    if os.path.exists(temp_dir):
        # Walk through the directory from bottom-up (topdown=False) to ensure
        # files are deleted before their parent directories.
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir) # Finally, remove the top-level temporary directory
        print("Cleanup complete. Temporary files and directory removed.")
    else:
        print("Temporary directory already removed or never created.")

    print("\nScript finished. Remember the warning about backups for real-world usage!")
