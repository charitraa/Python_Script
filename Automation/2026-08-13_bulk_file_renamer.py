import os
import shutil
import sys

def bulk_rename():
    """
    Guides the user through renaming multiple files in a specified directory.
    It allows for string replacement, adding prefixes, and adding suffixes to filenames.
    The script first previews the proposed changes and asks for user confirmation
    before performing any actual file operations, ensuring safety.
    """
    print("--- Bulk File Renamer ---")
    print("This script will help you rename files in a chosen directory.")
    print("You can replace text, add prefixes, or add suffixes to your filenames.")

    # 1. Get the target directory from the user.
    # Loop until a valid directory path is provided.
    while True:
        target_directory = input("\nEnter the directory path where files are located: ").strip()
        if not os.path.isdir(target_directory):
            print(f"Error: '{target_directory}' is not a valid directory or does not exist. Please try again.")
        else:
            break

    # 2. Get renaming rules: substring replacement, prefix, and suffix.

    # Substring replacement: find a specific string and replace it with another.
    print("\n--- Substring Replacement (Optional) ---")
    print("Leave 'Substring to find' empty if you don't want to replace any text.")
    old_substring = input("Enter the substring to find in filenames: ").strip()
    new_substring = ""
    if old_substring:
        new_substring = input(f"Enter the substring to replace '{old_substring}' with: ").strip()
        # If new_substring is empty, it effectively removes old_substring.

    # Prefix addition: add text to the beginning of the filename (before the original name, after directory path).
    print("\n--- Prefix Addition (Optional) ---")
    add_prefix = input("Enter a prefix to add to filenames (e.g., 'ARCHIVED_', leave empty for none): ").strip()

    # Suffix addition: add text to the end of the filename (before the file extension).
    print("\n--- Suffix Addition (Optional) ---")
    add_suffix = input("Enter a suffix to add to filenames (e.g., '_FINAL', leave empty for none): ").strip()

    # List to store tuples of (old_file_path, new_file_path) for proposed changes.
    proposed_changes = []

    # Iterate through all entries (files and directories) in the target directory.
    for filename in os.listdir(target_directory):
        old_filepath = os.path.join(target_directory, filename)

        # Only process actual files, not subdirectories.
        if os.path.isfile(old_filepath):
            new_filename = filename # Start with the original filename for this file.

            # Apply substring replacement if 'old_substring' was provided.
            if old_substring:
                new_filename = new_filename.replace(old_substring, new_substring)

            # Split the filename into its base name and extension.
            # This is crucial for adding prefix/suffix correctly before the extension.
            name_without_ext, extension = os.path.splitext(new_filename)

            # Apply prefix if 'add_prefix' was provided.
            if add_prefix:
                name_without_ext = add_prefix + name_without_ext
            
            # Apply suffix if 'add_suffix' was provided.
            if add_suffix:
                name_without_ext = name_without_ext + add_suffix
            
            # Reconstruct the new filename by combining the modified base name and original extension.
            new_filename = name_without_ext + extension

            new_filepath = os.path.join(target_directory, new_filename)

            # If the calculated new filename is different from the old one, add it to proposed changes.
            if old_filepath != new_filepath:
                proposed_changes.append((old_filepath, new_filepath))

    # If no changes are proposed after checking all files, inform the user and exit.
    if not proposed_changes:
        print("\nNo files found to rename or no changes proposed based on your input criteria.")
        return

    # 3. Preview proposed changes to the user for review.
    print("\n--- Proposed Renames ---")
    print("The following changes will be applied:")
    for old_path, new_path in proposed_changes:
        print(f"  '{os.path.basename(old_path)}' -> '{os.path.basename(new_path)}'")
    
    # 4. Ask for user confirmation before proceeding with actual renames.
    confirmation = input("\nDo you want to proceed with these renames? (yes/no): ").strip().lower()

    if confirmation == "yes":
        print("\n--- Executing Renames ---")
        successful_renames = 0
        skipped_renames = 0
        # Iterate through the proposed changes and perform the rename operation.
        for old_path, new_path in proposed_changes:
            try:
                # Check if the target filename already exists and is not the same as the source file.
                # This prevents accidentally overwriting existing files that were not part of the rename source.
                if os.path.exists(new_path) and old_path != new_path:
                    print(f"Skipping '{os.path.basename(old_path)}': Target name '{os.path.basename(new_path)}' already exists. "
                          "Please rename manually if you wish to overwrite.")
                    skipped_renames += 1
                    continue
                
                # Perform the actual file rename using os.rename().
                os.rename(old_path, new_path)
                print(f"Renamed: '{os.path.basename(old_path)}' -> '{os.path.basename(new_path)}'")
                successful_renames += 1
            except OSError as e:
                # Catch any operating system errors during renaming (e.g., permissions, file in use).
                print(f"Error renaming '{os.path.basename(old_path)}': {e}")
                skipped_renames += 1
        
        print(f"\n--- Renaming Complete ---")
        print(f"Successfully renamed {successful_renames} files.")
        if skipped_renames > 0:
            print(f"Skipped {skipped_renames} files due to errors or existing target names.")
    else:
        print("Renaming cancelled by user.")

if __name__ == "__main__":
    # --- Example Usage ---
    # This section demonstrates how to use the script by setting up a temporary
    # directory with dummy files and providing clear instructions for user input.

    print("\n--- Running Example Setup ---")
    test_dir = "temp_rename_test_files"
    
    # 1. Create a temporary directory for testing purposes.
    # If the directory already exists from a previous run, it will be removed and recreated.
    if os.path.exists(test_dir):
        print(f"Removing existing temporary directory: '{test_dir}'")
        shutil.rmtree(test_dir) 
    os.makedirs(test_dir)
    print(f"Created a fresh temporary directory: '{test_dir}'")

    # 2. Create some dummy files inside the temporary directory.
    dummy_files = [
        "meeting_notes_draft_2023.txt",
        "meeting_notes_draft_2024.txt",
        "image_projectA_draft_01.jpg",
        "image_projectA_draft_02.png",
        "old_document.pdf",
        "report_template.docx"
    ]
    for filename in dummy_files:
        with open(os.path.join(test_dir, filename), 'w') as f:
            f.write(f"This is a dummy file named {filename}\n")
    print(f"Created {len(dummy_files)} dummy files in '{test_dir}' for testing.")

    print("\n--- How to Test the Renamer ---")
    print(f"When the script prompts for the 'directory path', please enter: '{test_dir}'")
    
    print("\nHere are some renaming scenarios you can try:")
    print("--------------------------------------------------------------------------")
    print("Scenario 1: Replace 'draft' with 'final'")
    print("  - Substring to find: 'draft'")
    print("  - Substring to replace with: 'final'")
    print("  - Prefix: (leave empty)")
    print("  - Suffix: (leave empty)")
    print("  (This will change 'meeting_notes_draft_2023.txt' to 'meeting_notes_final_2023.txt', etc.)")
    print("--------------------------------------------------------------------------")
    print("Scenario 2: Add a prefix 'ARCHIVED_' to all remaining files (run after Scenario 1 for best effect)")
    print("  - Substring to find: (leave empty)")
    print("  - Substring to replace with: (leave empty)")
    print("  - Prefix: 'ARCHIVED_'")
    print("  - Suffix: (leave empty)")
    print("  (This will change 'meeting_notes_final_2023.txt' to 'ARCHIVED_meeting_notes_final_2023.txt', etc.)")
    print("--------------------------------------------------------------------------")
    print("Scenario 3: Change '_document.pdf' to '_report.docx' and add a suffix '_updated'")
    print("  - Substring to find: '.pdf'")
    print("  - Substring to replace with: '.docx'")
    print("  - Prefix: (leave empty)")
    print("  - Suffix: '_updated'")
    print("  (This would apply to 'old_document.pdf'. Note the order of operations: replace, then add suffix before extension.)")
    print("--------------------------------------------------------------------------")

    input("\nPress Enter to start the interactive renaming script...")
    
    # Call the main renaming function. The user will provide input interactively.
    bulk_rename()

    print(f"\n--- Example Usage Finished ---")
    print(f"You can now inspect the directory '{test_dir}' to see the changes.")
    
    # Offer to clean up the temporary directory.
    cleanup = input("Do you want to delete the temporary test directory and its files now? (yes/no): ").strip().lower()
    if cleanup == "yes":
        shutil.rmtree(test_dir)
        print(f"Temporary directory '{test_dir}' and its contents deleted.")
    else:
        print(f"Please remember to delete '{test_dir}' manually when you are done testing.")
