"""
A standalone Python script to organize files in a specified directory by their file extensions.

It creates subdirectories based on the file extension (e.g., 'PDF', 'JPG', 'TXT')
and moves the respective files into these newly created folders. Files without an
extension are moved into a 'NO_EXTENSION' folder.

The script can optionally move files to a different destination directory and
ignore certain file extensions during organization.
"""

import os
import shutil
import sys

def organize_files(source_dir, destination_dir=None, ignore_extensions=None):
    """
    Organizes files in the `source_dir` into subdirectories based on their extensions.

    Args:
        source_dir (str): The path to the directory whose files are to be organized.
        destination_dir (str, optional): The path where organized folders/files will be created.
                                         If None, files are organized within the source_dir.
        ignore_extensions (list, optional): A list of file extensions (e.g., ['.py', '.ini'])
                                            to ignore during organization. Case-insensitive.
    """

    # --- 1. Validate and prepare directories ---
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory.")
        return

    # If no destination is specified, use the source directory itself
    if destination_dir is None:
        destination_dir = source_dir
    else:
        # Create destination directory if it doesn't exist
        if not os.path.exists(destination_dir):
            try:
                os.makedirs(destination_dir)
                print(f"Created destination directory: '{destination_dir}'")
            except OSError as e:
                print(f"Error: Could not create destination directory '{destination_dir}': {e}")
                return
        elif not os.path.isdir(destination_dir):
            print(f"Error: Destination path '{destination_dir}' exists but is not a directory.")
            return

    # Prepare ignore_extensions for efficient lookup (lowercase, no leading dot)
    if ignore_extensions is None:
        ignore_extensions = set()
    else:
        ignore_extensions = {ext.strip('.').lower() for ext in ignore_extensions}
        print(f"Ignoring files with extensions: {', '.join(sorted(ignore_extensions))}")

    print(f"\n--- Starting file organization ---")
    print(f"Source: '{source_dir}'")
    print(f"Destination: '{destination_dir}'\n")

    files_organized_count = 0
    files_skipped_count = 0

    # --- 2. Iterate through items in the source directory ---
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)

        # Skip directories and non-file items
        if os.path.isfile(source_path):
            filename_without_ext, extension = os.path.splitext(item)

            # Determine the folder name based on the extension
            # Remove leading dot and convert to uppercase for consistency (e.g., 'PDF', 'JPG')
            # Use 'NO_EXTENSION' for files without any extension
            folder_name = extension[1:].upper() if extension else "NO_EXTENSION"

            # Check if the extension should be ignored
            if folder_name.lower() in ignore_extensions:
                print(f"Skipping '{item}' (ignored extension '{extension}').")
                files_skipped_count += 1
                continue

            # Construct the path to the target subdirectory
            target_folder_path = os.path.join(destination_dir, folder_name)

            # Create the target subdirectory if it doesn't exist
            if not os.path.exists(target_folder_path):
                try:
                    os.makedirs(target_folder_path)
                    print(f"Created directory: '{target_folder_path}'")
                except OSError as e:
                    print(f"Error creating directory '{target_folder_path}': {e}. Skipping '{item}'.")
                    files_skipped_count += 1
                    continue

            # --- 3. Handle potential duplicate filenames in the destination folder ---
            dest_file_path = os.path.join(target_folder_path, item)
            base_filename = filename_without_ext
            duplicate_counter = 0

            while os.path.exists(dest_file_path):
                duplicate_counter += 1
                # Append '_copy_X' before the extension to create a unique name
                if extension:
                    new_filename = f"{base_filename}_copy_{duplicate_counter}{extension}"
                else: # For files without an extension
                    new_filename = f"{base_filename}_copy_{duplicate_counter}"
                dest_file_path = os.path.join(target_folder_path, new_filename)
                print(f"Warning: File '{item}' already exists in '{target_folder_path}'. Trying to rename to '{new_filename}'.")

            # --- 4. Move the file ---
            try:
                shutil.move(source_path, dest_file_path)
                print(f"Moved '{item}' to '{target_folder_path}'")
                files_organized_count += 1
            except shutil.Error as e:
                print(f"Error moving '{item}' to '{target_folder_path}': {e}. Skipping.")
                files_skipped_count += 1
            except OSError as e: # Catch other potential OS errors like permission issues
                print(f"OS Error moving '{item}' to '{target_folder_path}': {e}. Skipping.")
                files_skipped_count += 1

    # --- 5. Print summary ---
    print("\n--- Organization Complete ---")
    print(f"Files organized: {files_organized_count}")
    print(f"Files skipped: {files_skipped_count}")
    if files_organized_count == 0 and files_skipped_count == 0:
        print("No files found to organize or all items were directories.")


if __name__ == "__main__":
    # --- Example Usage ---
    # This block demonstrates how to use the organize_files function.
    # It creates a temporary directory with some dummy files,
    # organizes them, and then cleans up the temporary directory.

    test_dir_name = "test_organizer_files"
    dummy_files = {
        "document.txt": "This is a text document.",
        "image.jpg": "Fake image content.",
        "report.pdf": "Fake PDF content.",
        "archive.zip": "Fake ZIP content.",
        "script.py": "# Python script",
        "README": "File with no extension.",
        "another_document.txt": "Another text document.", # To test duplicate handling
        "LICENSE.md": "Markdown file.",
        "config.json": "{'key': 'value'}",
        "important_note.TXT": "Uppercase extension test."
    }

    # Create a temporary directory for testing
    if not os.path.exists(test_dir_name):
        os.makedirs(test_dir_name)
        print(f"Created temporary test directory: '{test_dir_name}'")

    # Create dummy files inside the temporary directory
    for filename, content in dummy_files.items():
        file_path = os.path.join(test_dir_name, filename)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Created dummy file: '{file_path}'")

    print("\n--- Running file organizer example ---")
    # Call the organizer function
    # You can specify a different destination directory like:
    # organize_files(test_dir_name, destination_dir="organized_files_output")
    # or ignore specific extensions:
    # organize_files(test_dir_name, ignore_extensions=['.py', '.json'])

    organize_files(test_dir_name, ignore_extensions=['.py'])

    print(f"\n--- Cleaning up temporary test directory '{test_dir_name}' ---")
    # Clean up: Remove the temporary directory and all its contents
    try:
        if os.path.exists(test_dir_name):
            shutil.rmtree(test_dir_name)
            print(f"Successfully removed '{test_dir_name}' and its contents.")
    except OSError as e:
        print(f"Error during cleanup of '{test_dir_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during cleanup: {e}")
