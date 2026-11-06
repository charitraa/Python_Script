import os
import shutil
import sys

"""
This script helps organize files on your desktop (or any specified directory)
by moving them into categorized subfolders within a new 'Desktop_Cleaned'
directory. It identifies common file types (images, documents, videos, etc.)
and places them into respective folders like 'Images', 'Documents', 'Videos',
and 'Others' for unknown types.

It's designed to be safe:
1. It prompts for confirmation before making any changes.
2. All organized files are moved into a dedicated 'Desktop_Cleaned' folder,
   keeping your main desktop tidy and all moved files in one clear location.
3. Existing directories on your desktop are skipped to prevent accidental
   reorganization of your personal folders.
4. It handles duplicate filenames by renaming them (e.g., 'report.pdf' becomes 'report_1.pdf').
5. Provides feedback on what files are moved and any errors encountered.
"""

# Dictionary mapping common file extensions to their respective category folder names.
# This makes it easy to add or modify categories.
FILE_CATEGORIES = {
    # Image files
    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'): 'Images',
    # Document files (Word, OpenOffice Text)
    ('.doc', '.docx', '.odt', '.rtf'): 'Documents',
    # PDF files
    ('.pdf',): 'PDFs',
    # Spreadsheet files (Excel, OpenOffice Calc, CSV)
    ('.xls', '.xlsx', '.ods', '.csv'): 'Spreadsheets',
    # Presentation files (PowerPoint, OpenOffice Impress)
    ('.ppt', '.pptx', '.odp'): 'Presentations',
    # Video files
    ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'): 'Videos',
    # Audio files
    ('.mp3', '.wav', '.aac', '.flac', '.ogg'): 'Audio',
    # Archive files (ZIP, RAR, 7z, TAR, GZ, BZ2)
    ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'): 'Archives',
    # Executable files (Windows, macOS, Linux package formats)
    ('.exe', '.msi', '.deb', '.rpm', '.app', '.dmg'): 'Executables',
    # Text files (plain text, markdown, log files)
    ('.txt', '.log', '.md'): 'Text Files',
    # Common code/script files
    ('.py', '.html', '.css', '.js', '.json', '.xml', '.java', '.c', '.cpp', '.h'): 'Code Files',
    # Windows shortcut files
    ('.lnk',): 'Shortcuts',
    # Disk image files (ISO, IMG)
    ('.iso', '.img'): 'Disk Images',
    # Font files
    ('.ttf', '.otf', '.woff', '.woff2'): 'Fonts',
}

def get_file_category(filename):
    """
    Determines the category for a given filename based on its extension.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The name of the category folder (e.g., 'Images', 'Documents', 'Others').
    """
    # Split the filename into base and extension (e.g., 'document.pdf' -> ('document', '.pdf'))
    _, ext = os.path.splitext(filename)
    ext = ext.lower() # Convert extension to lowercase for case-insensitive matching

    # Iterate through the defined categories to find a match
    for extensions, category in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    # If no specific category is found, place it in 'Others'
    return 'Others'

def clean_desktop(target_dir):
    """
    Organizes files in the specified directory into subfolders based on file type.
    All organized files are moved into a 'Desktop_Cleaned' directory within the target_dir,
    with further subfolders like 'Images', 'Documents', etc.

    Args:
        target_dir (str): The path to the directory to be cleaned.
    """
    print(f"\n--- Starting Desktop Cleanup for: {target_dir} ---")

    # Define the path for the main directory where cleaned files will reside.
    # This ensures all organized files are grouped together.
    cleaned_parent_dir = os.path.join(target_dir, 'Desktop_Cleaned')
    
    # Create the 'Desktop_Cleaned' directory if it doesn't already exist.
    # exist_ok=True prevents an error if the directory already exists.
    os.makedirs(cleaned_parent_dir, exist_ok=True)
    print(f"All organized files will be moved into: {cleaned_parent_dir}")

    items_processed = 0
    items_skipped = 0
    errors_encountered = 0

    # Iterate over all items (files and directories) in the target directory
    for item_name in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item_name)

        # Skip the 'Desktop_Cleaned' directory itself to avoid processing its contents
        # or attempting to move it, which could lead to errors or infinite loops.
        if os.path.abspath(item_path) == os.path.abspath(cleaned_parent_dir):
            print(f"  Skipped the cleaning directory itself: '{item_name}'")
            items_skipped += 1
            continue

        if os.path.isfile(item_path):
            # Determine the category for the current file
            category = get_file_category(item_name)
            
            # Define the destination folder (e.g., 'Desktop_Cleaned/Images')
            destination_folder = os.path.join(cleaned_parent_dir, category)
            # Define the full path for the file in its new location
            destination_path = os.path.join(destination_folder, item_name)

            # Create the category-specific subfolder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)

            try:
                # Handle potential duplicate filenames in the destination folder.
                # If a file with the same name already exists, append a counter.
                if os.path.exists(destination_path):
                    base, ext = os.path.splitext(item_name)
                    counter = 1
                    # Keep incrementing counter until a unique filename is found
                    while os.path.exists(os.path.join(destination_folder, f"{base}_{counter}{ext}")):
                        counter += 1
                    new_item_name = f"{base}_{counter}{ext}"
                    destination_path = os.path.join(destination_folder, new_item_name)
                    print(f"  Conflict: Renaming '{item_name}' to '{new_item_name}' for move to '{category}'")
                
                # Move the file from its original location to the new categorized location
                shutil.move(item_path, destination_path)
                print(f"  Moved '{item_name}' to '{category}'")
                items_processed += 1
            except Exception as e:
                # Catch any errors during the move operation (e.g., permission denied)
                print(f"  ERROR: Could not move '{item_name}' to '{category}'. Reason: {e}")
                errors_encountered += 1
        elif os.path.isdir(item_path):
            # The script is designed to clean loose files, so existing directories are skipped.
            print(f"  Skipped directory: '{item_name}'")
            items_skipped += 1
        else:
            # Handle other uncommon item types (e.g., symbolic links that are not files/dirs)
            print(f"  Skipped unknown item type: '{item_name}'")
            items_skipped += 1

    print(f"\n--- Cleanup Finished ---")
    print(f"  {items_processed} files organized.")
    print(f"  {items_skipped} items skipped (includes directories and the 'Desktop_Cleaned' folder).")
    if errors_encountered > 0:
        print(f"  {errors_encountered} errors encountered during move operations. Please check permissions.")
    print(f"All cleaned files are now in subfolders within '{cleaned_parent_dir}'")
    print("Consider reviewing the 'Others' folder if you have custom file types that were not categorized.")


if __name__ == "__main__":
    # Determine the default desktop path for the current user across different OS.
    # `os.path.expanduser('~')` gets the user's home directory.
    default_desktop_path = os.path.expanduser('~/Desktop')

    print("Desktop Cleaner Script")
    print("----------------------")
    print("This script helps organize loose files on your desktop (or any specified directory)")
    print("by moving them into categorized subfolders.")
    print("All organized files will be placed into a new folder named 'Desktop_Cleaned'")
    print("within the target directory.")

    while True:
        print(f"\nYour current default desktop path is: '{default_desktop_path}'")
        user_input = input("Do you want to clean this desktop path? (yes/no/change path): ").lower().strip()

        if user_input == 'yes':
            clean_desktop(default_desktop_path)
            break # Exit the loop after cleaning
        elif user_input == 'change path':
            new_path = input("Enter the full path to the directory you want to clean: ").strip()
            # Check if the provided path is a valid directory
            if os.path.isdir(new_path):
                clean_desktop(new_path)
                break # Exit the loop after cleaning
            else:
                print(f"Error: The path '{new_path}' does not exist or is not a directory. Please try again.")
        elif user_input == 'no':
            print("Exiting script. No changes were made.")
            sys.exit(0) # Exit the script cleanly
        else:
            print("Invalid input. Please type 'yes', 'no', or 'change path'.")
